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

# Importing the 'search_tool' module's Haystack Pipeline Implementation
from .search_tool import search_pipe




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
    You are a citation-checking assistant. Given a "claim" and a "context", verify whether the claim is supported by the context or by external sources. Return exactly this format:

    {
      "claim_valid": <true|false>,
      "citations": [
        {
          "title": <string>,
          "url": <string>,
          "snippet": <excerpt supporting or refuting the claim>
        },
        ... zero or more items
      ]
    }

    ### Example 1 (Generic, True)
    Sample Input:
    {
      "claim": "Paris is the capital of France.",
      "context": "France is a country in Europe; its capital city is Paris."
    }
    ---
    Sample Output:
    {
      "claim_valid": true,
      "citations": [
        {
          "title": "France capital city information",
          "url": "https://example.com/france",
          "snippet": "France's capital is Paris."
        }
      ]
    }

    ### Example 2 (Generic, False)
    Sample Input:
    {
      "claim": "Mount Everest is the tallest mountain in Africa.",
      "context": "Mount Everest is the highest mountain above sea level, located in the Himalayas in Asia."
    }
    ---
    Sample Output:
    {
      "claim_valid": false,
      "citations": [
        {
          "title": "Mount Everest location and height",
          "url": "https://example.com/everest",
          "snippet": "Mount Everest is located in the Himalayas, in Asia, and is not in Africa."
        }
      ]
    }

    ### Example 3 (Domain: Quick-Commerce, True)
    Sample Input:
    {
      "claim": "Swiggy Instamart delivery is free only for Swiggy One members.",
      "context": "Currently, free delivery on Instamart is available exclusively to users subscribed to Swiggy One; all other users are charged per-order delivery fees."
    }
    ---
    Sample Output:
    {
      "claim_valid": true,
      "citations": [
        {
          "title": "Swiggy Instamart pricing",
          "url": "https://example.com/swiggy",
          "snippet": "delivery is free only for Swiggy One users; others have to pay a fee."
        }
      ]
    }

    ### Now please verify:
    Sample Input:
    { "claim": "...", "context": "..." }

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
citation_agent.__name__ = "claim_context_based_citation_tool"
citation_agent.__doc__ = "Does a web search, extract necessary information and return a formatted citation for a given claim-context pair."
citation_agent.connection_timeout = 60
citation_agent.invocation_timeout = 60



