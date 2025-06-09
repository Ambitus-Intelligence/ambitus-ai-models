import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.components.agents import Agent
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo
from haystack.utils import Secret
import traceback

# Load .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_market_data_agent() -> Agent:
    """Create and return a configured Haystack Agent for market data"""
    server_info = SSEServerInfo(base_url="http://localhost:8000")

    market_tool = MCPTool(name="search_tool", server_info=server_info)
    tools = [market_tool]

    system_prompt = """
You are MarketDataAgent, an AI assistant specialized in gathering and summarizing market statistics and emerging trends within a given domain.

Your objective is to provide a structured overview of key market dynamics.

Guidelines:
1. Use Only Trusted Sources: Prioritize financial APIs, market intelligence reports, trend data, and official statistics.
2. Organize Information: Return a JSON object with the following structure:
{
  "domain": "<domain name>",
  "market_size": {
    "value": "<e.g., 35B USD>",
    "year": "<most recent year available>",
    "sources": ["<url1>", "<url2>"]
  },
  "growth_rate": {
    "value": "<e.g., 12% CAGR>",
    "period": "<e.g., 2023-2028>",
    "sources": ["<url1>", "<url2>"]
  },
  "key_trends": [
    {
      "trend": "<brief summary of trend>",
      "sources": ["<url1>", "<url2>"]
    }
  ],
  "notes": "<any additional relevant insights or qualifiers>"
}
3. Avoid Speculation: Only include what can be found from reliable data sources.
4. Use JSON Only: No narrative outside the JSON.
"""

    return Agent(
        chat_generator=OpenAIChatGenerator(
            model="gpt-4o-mini",
            api_key=Secret.from_token(OPENAI_API_KEY),
        ),
        tools=tools,
        system_prompt=system_prompt,
    )


def run_market_data_agent(domain: str) -> Dict[str, Any]:
    """
    Execute market research for a given domain using Haystack Agent

    Args:
        domain (str): Market domain to analyze

    Returns:
        Dict[str, Any]: Result dictionary with success flag, data or error
    """
    try:
        if not domain or not isinstance(domain, str):
            return {
                "success": False,
                "error": "Invalid or missing 'domain' parameter.",
                "raw_response": None
            }

        agent = create_market_data_agent()

        user_message = f"""
        Provide up-to-date market statistics and trend analysis for the "{domain}" industry.
        Include market size, growth rate, key trends, and data sources.
        Summarize your findings in the structured JSON format specified in the system prompt.
        """

        # Execute agent
        response = agent.run(messages=[ChatMessage.from_user(user_message.strip())])

        # Get final message
        final_message = response.get("messages", [])[-1].text if response.get("messages") else None

        if not final_message:
            return {
                "success": False,
                "error": "Agent did not return a message.",
                "raw_response": None
            }

        try:
            # Try to parse as JSON
            market_data = json.loads(final_message)
            return {
                "success": True,
                "data": market_data,
                "raw_response": final_message
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Agent returned invalid JSON.",
                "raw_response": final_message
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "traceback": traceback.format_exc(),
            "raw_response": None
        }
