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

def create_competitive_landscape_agent():
    """Factory function to create a configured competitive landscape agent"""
    server_info = SSEServerInfo(
        base_url="http://localhost:8000",
    )

    search_tool = MCPTool(name="search_tool", server_info=server_info)
    tools = [search_tool]

    system_prompt = """
You are CompetitiveLandscapeAgent, a specialized AI agent tasked with mapping competitors and their product/market positions within a given domain. Your goal is to identify key players, their offerings, and competitive positioning.

Follow these guidelines strictly:

1. **Use Trusted Sources Only**: Prioritize data from industry reports, company websites, business directories, and reputable market research sources.
2. **Structure Your Output**: Always return a valid JSON array with competitor objects containing:
   - `competitor`: Company name
   - `product`: Main product/service in the domain
   - `market_share`: Estimated market share (0.0 to 1.0, use 0.0 if unknown)
   - `note`: Brief description of their competitive position/strategy
   - `sources`: Array of URLs or sources where information was found

3. **Focus on the Domain**: Only include competitors that are relevant to the specified domain.
4. **Be Factual, Not Speculative**: Base market share estimates on available data, use 0.0 if no reliable data exists.
5. **Respond in JSON Only**: No explanation or commentary outside the JSON array.

Example output format:
[
  {
    "competitor": "Company A",
    "product": "Product X",
    "market_share": 0.15,
    "note": "Market leader with strong enterprise focus",
    "sources": ["https://example.com/market-report", "https://company-a.com/about"]
  },
  {
    "competitor": "Company B", 
    "product": "Product Y",
    "market_share": 0.08,
    "note": "Emerging player with innovative approach",
    "sources": ["https://company-b.com/about", "https://techcrunch.com/article"]
  }
]
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

def run_competitive_landscape_agent(industry_opportunity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the competitive landscape agent for a given industry opportunity.
    
    Args:
        industry_opportunity: Dict containing domain, score, rationale, and sources
        
    Returns:
        Dict containing the agent's response and metadata
    """
    try:
        agent = create_competitive_landscape_agent()
        
        domain = industry_opportunity.get("domain", "")
        score = industry_opportunity.get("score", 0.0)
        rationale = industry_opportunity.get("rationale", "")
        
        message = f"""Map the competitive landscape for the {domain} domain (opportunity score: {score}).
        
Context: {rationale}

Identify key competitors, their products, market positions, and competitive strategies in this domain."""
        
        response = agent.run(
            messages=[
                ChatMessage.from_user(text=message),
            ]
        )
        
        # Extract the final response
        final_message = response["messages"][-1].text
        
        # Try to parse as JSON
        try:
            competitors_data = json.loads(final_message)
            return {
                "success": True,
                "data": competitors_data,
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
