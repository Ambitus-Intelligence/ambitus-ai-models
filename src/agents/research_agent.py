import os
from dotenv import load_dotenv
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.components.agents import Agent
from haystack_integrations.tools.mcp import MCPTool, SSEServerInfo
from haystack.utils import Secret

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


server_info = SSEServerInfo(
        base_url="http://localhost:8000",
    )

search_tool = MCPTool(name="search_tool", server_info=server_info)

tools = [ search_tool ]

system_prompt = """
You are CompanyResearchAgent, a specialized AI agent tasked with gathering foundational data about a given company. Your goal is to create a concise, factually accurate profile of the company using available web resources and APIs like Crunchbase and Wikipedia.

Follow these guidelines strictly:

1. **Use Trusted Sources Only**: Prioritize data from Crunchbase (if available), Wikipedia, and official company websites.
2. **Structure Your Output**: Always return a valid JSON object with the following keys:
   - `name`: Full company name.
   - `industry`: Primary industry of operation.
   - `description`: A short paragraph (2-3 sentences) summarizing what the company does.
   - `products`: List of main products or services.
   - `headquarters`: City and country of the company's main office.
   - `sources`: List of URLs used to derive the above information.

3. **Be Factual, Not Speculative**: Do not infer or hallucinate details. Only include data supported by the sources.
4. **Deduplicate and Clean**: Ensure data (especially lists like `products`) are not redundant, overly generic, or repeated.
5. **Respond in JSON Only**: No explanation or commentary. Just the structured JSON output.

Your task begins once you receive the company name as input.
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
