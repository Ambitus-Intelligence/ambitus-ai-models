import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.components.agents import Agent
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo
from haystack.utils import Secret
from haystack.components.builders import PromptBuilder

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_market_gap_analysis_agent():
    """Factory function to create a configured market gap research agent"""
    server_info = SSEServerInfo(
        base_url="http://localhost:8000",
    )

    search_tool = MCPTool(name="search_tool", server_info=server_info)
    tools = [search_tool]

    system_prompt = """
    You are MarketGapAnalysisAgent, a specialized AI agent designed to identify strategic market gaps. Your purpose is to analyze and compare a company's profile against its competitors and the broader market landscape to uncover unmet customer needs and untapped opportunities.

    Follow these guidelines strictly:

    1. **Analyze Provided Inputs Explicitly**: Your analysis must be based exclusively on the data provided to you, which includes a company profile, a list of competitors, and market statistics. Do not use external web resources or prior knowledge.
    2. **Structure Your Output**: Always return a valid JSON object with the following keys:
    - `gap`: A concise string describing the specific unmet need or missing feature.
    - `impact`: A string indicating the potential market impact of this gap, rated as "High", "Medium", or "Low".
    - `evidence`: A short paragraph (2-3 sentences) explaining the reasoning for the identified gap, directly referencing the provided data (e.g., "Competitor X offers this feature, but the target company does not," or "Market stats show a growing demand for Y, which is not addressed by the company's current products.").
    - `source`: List of URLs used to derive the above information.

    3. **Be Logical and Evidential**: Do not infer or hallucinate details. Only include data supported by the sources.
    4. **Respond in JSON Only**: No explanation or commentary outside the JSON. Just the structured JSON output.

    Example output format:
    [{
        "gap": "Lack of an entry-level pricing tier for small businesses.",
        "impact": "High",
        "evidence": "Market statistics indicate that 45 percentage of the target market consists of small businesses with fewer than 10 employees. All listed competitors offer a dedicated 'Basic' or 'Starter' plan, while the company's lowest-priced product is targeted at mid-market clients.",
        "source": "Market Stats Report, Competitor List"
    }]
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

def run_market_gap_analysis_agent(incoming_company_stats: Dict[str,Any]) -> Dict[str,Any]:
    """
    Run the company research agent for a given company name.
    
    Args:
        company profile: Company's market domain.
        competitor list: list of company's competitors.
        market stats: some statistical data about the market.
        
    Returns:
        Dict containing the agent's response and metadata
    """
    try:
        agent = create_market_gap_analysis_agent()
        
        user_message = '''
        Analyze the following data to identify strategic market gaps. Base your analysis exclusively on this information and respond in the required JSON format.

        ### Company Profile
        - **Name:** {{ company_stats.company_profile.name }}
        - **Industry:** {{ company_stats.company_profile.industry }}
        - **Description:** {{ company_stats.company_profile.description }}
        - **Products:**
        {% for product in company_stats.company_profile.products %}
        - {{ product }}
        {% endfor %}
        - **Headquarters:** {{ company_stats.company_profile.headquarters }}
        - **Sources:** {% for source in company_stats.company_profile.sources %}{{ source }}{% if not loop.last %}, {% endif %}{% endfor %}

        ### Competitor Landscape
        {% for competitor in company_stats.competitor_list %}
        ---
        - **Competitor:** {{ competitor.competitor }}
        - **Product Focus:** {{ competitor.product }}
        - **Market Share:** {{ competitor.market_share }}%
        - **Note:** {{ competitor.note }}
        - **Sources:** {% for source in competitor.sources %}{{ source }}{% if not loop.last %}, {% endif %}{% endfor %}
        {% endfor %}

        ### Market Statistics
        - **Market Size (USD):** {{ company_stats.market_stats.market_size_usd }}
        - **CAGR:** {{ company_stats.market_stats.CAGR }}%
        - **Key Drivers:**
        {% for driver in company_stats.market_stats.key_drivers %}
        - {{ driver }}
        {% endfor %}
        - **Sources:** {% for source in company_stats.market_stats.sources %}{{ source }}{% if not loop.last %}, {% endif %}{% endfor %}

        Based on this data, identify the market gaps.
        '''
        template = user_message
        builder = PromptBuilder(template=template)
        result = builder.run(company_stats=incoming_company_stats)
        generated_user_message = result["prompt"]


        response = agent.run(
            messages=[
                ChatMessage.from_user(text=generated_user_message),
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

