# Library Import
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo, MCPToolset
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from typing import Any,Dict
from haystack.utils import Secret
import os
from dotenv import load_dotenv

from typing import List
from haystack import component, Document, Pipeline, SuperComponent
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import MultiFileConverter
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from duckduckgo_api_haystack import DuckduckgoApiWebSearch
from haystack.dataclasses import ChatMessage, ToolCall
from haystack.components.tools import ToolInvoker
from haystack.tools import Tool
from haystack.tools import ComponentTool




load_dotenv()
key = os.getenv("OPENAI_API_KEY")

# web search pipeline made into a component(superComponent) made into a tool(componentTool)


# Citation_agent
def citation_agent(claim: str, context: str) -> dict[str, Any]:
    """
    Generate a citation for a given claim and context.

    Args:
        claim: The claim to be cited.
        context: The context or source of the claim.
        
    Returns:
        Dict containing the citation information
    """
    @component
    class DocumentFormatter:
        """
        Takes a list of Documents and returns two lists of strings:
          - `sources`:  ["Source 1: <url1>", "Source 2: <url2>", …]
          - `information`: ["Information 1: <content1>", …]
        """
        @component.output_types(sources=List[str], information=List[str])
        def run(self, documents: List[Document]):
            sources: List[str] = []
            information: List[str] = []
            for idx, doc in enumerate(documents, start=1):
                url = doc.meta.get("url", "<no-url>")
                sources.append(f"Source {idx}: {url}")
                information.append(f"Information {idx}: {doc.content}")
            return {"sources": sources, "information": information}
        

    # Search Pipeline
    search_pipe = Pipeline()

    search_pipe.add_component("search", DuckduckgoApiWebSearch(top_k=3, backend="auto"))
    search_pipe.add_component("fetcher", LinkContentFetcher(timeout=3, raise_on_failure=False, retry_attempts=2))
    search_pipe.add_component("converter", MultiFileConverter())
    search_pipe.add_component("formatter", DocumentFormatter())

    search_pipe.connect("search.links", "fetcher.urls")
    search_pipe.connect("fetcher.streams", "converter.sources")
    search_pipe.connect("converter.documents", "formatter.documents")



    search_pipe_component = SuperComponent(
        pipeline=search_pipe
    )

    search_tool = ComponentTool(
        component=search_pipe_component,
        name="search_tool", 
        description="Search the web for current information on any topic."
    )
    
    
    llm = OpenAIChatGenerator(
        model="o4-mini",
        api_key=Secret.from_token(token=key)
    )
    
    # server_info = SSEServerInfo(
    #     base_url="http://localhost:8000",
    # )

    # search_tool = MCPTool(name="search_tool", server_info=server_info)
    tools = [search_tool]

    agent = Agent(
        chat_generator = llm,
        tools = tools
    )

    # Prompting the Agent
    system_prompt = """
    You'll be given two strings, 1. claim , 2. context.
    You have to verify whether the claim is valid based on the context.
    And, return the response in output format only.
    ---
    Input format:
    {
      "claim":      { "type": "string", "description": "Statement to be verified" },
      "context":    { "type": "string", "description": "Supplementary text or background" },
    }
    ---
    Output format:
    {
      "claim_valid": { "type": "boolean", "description": "True if at least one citation supports the claim" },
      "citations": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "title":   { "type": "string", "description": "Page or article title" },
            "url":     { "type": "string", "description": "Source URL" },
            "snippet": { "type": "string", "description": "Excerpt showing the claim support" }
          },
          "required": ["url", "snippet"]
        }
      },
    }
    ---
    Sample Input:
    {
      "claim": "Blinkit offers 10‑minute grocery delivery in Mumbai.",
      "context": "Blinkit operates in 25 Indian cities including Mumbai, Delhi, Bangalore. It promises grocery delivery within 10 minutes of order placement in major metros."
    }
    Sample Output:
    {
      "claim_valid": true,
      "citations": [
        {
          "title": "Blinkit operates in 25 Indian cities including Mumbai, Delhi, Bangalore",
          "url": "https://example.com/article",
          "snippet": "It promises grocery delivery within 10 minutes of order placement in major metros."
        }
      ]
    }
    """

    sys = ChatMessage.from_system(system_prompt)
    claim_ip = ChatMessage.from_user(claim)
    context_ip = ChatMessage.from_user(context)
    messages = [sys,claim_ip,context_ip]

    agent.warm_up()

    try:
        response = agent.run(messages=messages)
        return response['messages'][-1].texts
    except Exception as e:
        return {
            "claim_valid": False,
            "claim": claim,
            "error": str(e)
        }

# Configuring function metadata for FastMCP
citation_agent.__name__ = "citation_agent_tool"
citation_agent.__doc__ = "Generate a citation for a given claim against a provided context."



