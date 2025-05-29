import os
import json
from typing import Dict, Any, List # Added List
from dotenv import load_dotenv
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.components.agents import Agent
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo
from haystack.utils import Secret

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_industry_analysis_agent():
    """
    Factory function to create an agent that analyzes a company's profile 
    and suggests ranked industry/domain expansion opportunities.
    """
    
    """ server_info = SSEServerInfo(
        base_url="http://localhost:8000", # Assuming MCP server is running locally
    )

    search_tool = MCPTool(name="search_tool", server_info=server_info)
    tools = [search_tool] """

    system_prompt = """
You are IndustryAnalysisAgent, an AI expert in market strategy and domain expansion.

Your task is to analyze a structured company profile and suggest a ranked list of promising industries/domains the company could expand into.

Guidelines:
1. Consider current industry, product strengths, technological capabilities, market position, and geography.
2. Rank at least 3–5 high-potential domains. Assign each a `score` (0.0–1.0) representing strategic fit and opportunity.
3. For each domain, include a 1–2 sentence `rationale` explaining why it's a good fit.
4. Use any provided `sources` to support or reference your rationale if applicable.
5. Return only a JSON list in the following format:

[
  { "domain": "Retail Tech", "score": 0.92, "rationale": "Company’s strong e-commerce platform could pivot to retail analytics.", "sources": ["https://example.com"] },
  ...
]

Be factual and logical. Avoid hallucination or baseless speculation. Respond only with the structured JSON list.
"""

    # Create the agent
    agent = Agent(
        chat_generator=OpenAIChatGenerator(
            model="o4-mini", 
            api_key=Secret.from_token(OPENAI_API_KEY)
        ),
        tools=[],
        system_prompt=system_prompt,
    )
    
    return agent

def run_company_research_agent(company_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the Industry Analysis Agent for a given structured company profile.

    Args:
        company_profile: Structured JSON with company details.

    Returns:
        Dict with success status, parsed data or error, and raw output.
    """
    try:
        agent = create_industry_analysis_agent()

        input_json = json.dumps(company_profile, indent=2)

        response = agent.run(
            messages=[
                ChatMessage.from_user(text=f"Analyze the following company profile:\n{input_json}")
            ]
        )

        final_message = response["messages"][-1].text
        
        # Try to parse as JSON
        try:
            output_data = json.loads(final_message)
            return {
                "success": True,
                "data": output_data,
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