# src/ambitus_ai_models/agents/researcher.py
from haystack.components.agents import Agent # Assuming this is the correct import for the Agent class
from haystack.core.component import Generator # Import base type for hinting
from haystack.core.component import ComponentTool # Import type for tools list

# Import the tool creation function
from src.ambitus_ai_models.tools.search import create_search_tool
# from src.ambitus_ai_models.tools.tech_extract import create_tech_extract_tool # If researcher uses this too


def create_researcher_agent(chat_generator: Generator) -> Agent:
    """
    Creates and configures the Researcher Agent.
    """
    # Create the specific tools this agent needs
    # Pass the agent's LLM to tools if the tools themselves use an LLM
    search_tool = create_search_tool(llm=chat_generator)
    # tech_extract_tool = create_tech_extract_tool(llm=chat_generator) # If researcher uses this too

    # Define the list of tools for this agent
    tools_for_this_agent = [search_tool] # Add other tools as needed

    # Define the system prompt for this agent
    system_prompt = """
You are a deep research assistant for a target industry/company.
You create comprehensive research reports to answer the user's questions.
Gather data on market trends, competitors, and dynamics.
Break the user question into smaller parts and answer each part separately using tools.
You MUST use the 'webSearch'-tool to answer any questions.
You MUST utilize the 'webSearch'-tool to search for information on the internet.
You perform multiple searches until you have the information you need to answer the question.
Make sure you research different aspects of the question.
Use markdown to format your response.
When you use information from the websearch results, cite your sources using markdown links.
It is important that you cite accurately, use links from 'webSearch' tool ONLY.
"""

    # Create the Agent instance
    agent = Agent(
        chat_generator=chat_generator,
        tools=tools_for_this_agent,
        system_prompt=system_prompt,
        exit_conditions=["text"], # Agent exits when it produces a final text response
        max_agent_steps=100,
        raise_on_tool_invocation_failure=True
    )

    # Agents might need warming up
    # agent.warm_up() # Consider warming up here or in the API startup

    return agent # Return the configured agent instance

# Similarly, create create_tech_extractor_agent() in tech_extractor.py