import os
import json
import traceback
from typing import Dict, Any
from dotenv import load_dotenv

from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.agents import Agent
from haystack.utils import Secret
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo

# environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_opportunity_agent():
    """
    Factory function to create the opportunity_agent for strategic growth opportunities.
    """
    system_prompt = """
You are OpportunityAgent, an expert business strategist AI.

Your goal is to analyze structured data on market gaps, company capabilities, and competitive insights, then suggest high-impact, validated growth opportunities.

Instructions:
1. Use the provided `market_gaps` list to identify unmet needs or pain points in the market.
2. For each identified gap, generate a relevant business opportunity. Focus on feasibility, strategic value, and novelty.
3. Use the `search_tool` to find real, working links or sources that support each opportunity — no hallucinations.
4. Each item must include:
   - "title": short name for the opportunity
   - "priority": High | Medium | Low based on strategic value
   - "description": 1–3 sentences on the value proposition and business logic
   - "sources": list of supporting evidence or links (real or from provided context)

Respond **only** with a JSON array in the format:
[
  {
    "title": "Launch AI Chatbot",
    "priority": "High",
    "description": "The company can leverage its NLP capabilities to offer a customer support chatbot. This fills a major gap in CX in the retail sector.",
    "sources": ["https://gartner.com/chatbots-2025"]
  },
  ...
]

Be realistic, prioritize feasibility and relevance. No speculative or generic output.
"""
    
    server_info = SSEServerInfo(base_url="http://localhost:8000")
    search_tool = MCPTool(name="search_tool", server_info=server_info)

    return Agent(
        chat_generator=OpenAIChatGenerator(
            model="o4-mini",
            api_key=Secret.from_token(OPENAI_API_KEY),
        ),
        tools=[search_tool],
        system_prompt=system_prompt,
    )

def run_opportunity_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate realistic, search-validated business opportunities from market gaps.
    """
    try:
        market_gaps = input_data.get("market_gaps")
        if not market_gaps or not isinstance(market_gaps, list):
            return {
                "success": False,
                "error": "Missing or invalid 'market_gaps'. Expected a list of strings.",
                "raw_response": None
            }

        agent = create_opportunity_agent()

        
        user_message = f"""
        Given the following market gaps:
        {json.dumps(market_gaps)}

        Generate 3–5 realistic growth opportunities.
        For each one, include title, priority, description, and sources (use the search_tool for links).
        Respond only in JSON array format.
        """

        result = agent.run(messages=[ChatMessage.from_user(user_message.strip())])
        final_message = result.get("messages", [])[-1].text if result.get("messages") else None

        if not final_message:
            return {
                "success": False,
                "error": "No response received from the agent.",
                "raw_response": None
            }

        # Parse the JSON safely
        try:
            parsed_data = json.loads(final_message)
            return {
                "success": True,
                "data": parsed_data,
                "raw_response": final_message
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Response is not valid JSON.",
                "raw_response": final_message
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "traceback": traceback.format_exc(),
            "raw_response": None
        }