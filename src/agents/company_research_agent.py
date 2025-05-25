import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.components.agents import Agent
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo
from haystack.utils import Secret

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_company_research_agent():
    """Factory function to create a configured company research agent"""
    server_info = SSEServerInfo(
        base_url="http://localhost:8000",
    )

    search_tool = MCPTool(name="search_tool", server_info=server_info)
    tools = [search_tool]

    system_prompt = """
You are CompanyResearchAgent, a specialized AI agent tasked with gathering foundational data about a given company. Your goal is to create a concise, factually accurate profile of the company using available web resources.

Follow these guidelines strictly:

1. **Use Trusted Sources Only**: Prioritize data from official company websites, Crunchbase, Wikipedia, and reputable business sources.
2. **Structure Your Output**: Always return a valid JSON object with the following keys:
   - `name`: Full company name.
   - `industry`: Primary industry of operation.
   - `description`: A short paragraph (2-3 sentences) summarizing what the company does.
   - `products`: List of main products or services (max 5 items).
   - `headquarters`: City and country of the company's main office.
   - `sources`: List of URLs used to derive the above information.

3. **Be Factual, Not Speculative**: Do not infer or hallucinate details. Only include data supported by the sources.
4. **Respond in JSON Only**: No explanation or commentary outside the JSON. Just the structured JSON output.

Example output format:
{
  "name": "Example Corp",
  "industry": "Technology",
  "description": "Example Corp is a leading technology company that develops innovative software solutions.",
  "products": ["Product A", "Product B", "Product C"],
  "headquarters": "San Francisco, USA",
  "sources": ["https://example.com", "https://wikipedia.org/wiki/Example_Corp"]
}
"""

    # Create the agent
    agent = Agent(
        chat_generator=OpenAIChatGenerator(
            model="o4-mini",
            api_key=Secret.from_token(OPENAI_API_KEY)
        ),
        tools=tools,
        system_prompt=system_prompt,
    )
    
    return agent

def run_company_research_agent(company_name: str) -> Dict[str, Any]:
    """
    Run the company research agent for a given company name.
    
    Args:
        company_name: Name of the company to research
        
    Returns:
        Dict containing the agent's response and metadata
    """
    try:
        agent = create_company_research_agent()
        
        response = agent.run(
            messages=[
                ChatMessage.from_user(text=f"Research and provide information about {company_name}"),
            ]
        )
        
        # Extract the final response
        final_message = response["messages"][-1].text
        
        # Try to parse as JSON
        try:
            company_data = json.loads(final_message)
            return {
                "success": True,
                "data": company_data,
                "raw_response": final_message
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response from agent",
                "raw_response": final_message
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_response": None
        }

