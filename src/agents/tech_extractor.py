# src/ambitus_ai_models/agents/tech_extractor.py

from haystack.agents import Agent # Assuming this is the correct import
from haystack.core.component import Generator
from haystack.core.component import ComponentTool

# Import the tool creation function(s) this agent will use
from src.ambitus_ai_models.tools.tech_extract import create_tech_extractor_tool
# from src.ambitus_ai_models.tools.search import create_search_tool # If this agent also uses search


def create_tech_extractor_agent(chat_generator: Generator) -> Agent:
    """
    Creates and configures the Tech Extractor Agent.
    """
    # Create the specific tools this agent needs
    # The TechExtractorTool doesn't inherently need the LLM, but pass it if its internal
    # logic might need it later, or just for consistency.
    tech_extract_tool = create_tech_extractor_tool() # LLM might not be needed here

    # Define the list of tools for this agent
    tools_for_this_agent = [tech_extract_tool]
    # If this agent also uses search:
    # search_tool = create_search_tool(llm=chat_generator)
    # tools_for_this_agent.append(search_tool)


    # Define the system prompt specific to guiding a tech extraction task
    system_prompt = """
You are a technology extraction specialist agent.
Your goal is to identify key technologies, novel terms, and their relationships within provided text documents.
You MUST use the 'TechExtractorTool' to perform the extraction.
Analyze the extraction results and present them in a clear, structured format, summarizing the key findings.
Do not invent technologies that are not present in the extraction tool's results.
""" # Define a prompt suitable for tech extraction


    # Create the Agent instance
    agent = Agent(
        chat_generator=chat_generator, # The LLM brain for this agent
        tools=tools_for_this_agent,
        system_prompt=system_prompt,
        exit_conditions=["text"], # Agent exits when it produces a final text response
        max_agent_steps=10, # Maybe fewer steps needed for extraction? Adjust as necessary.
        raise_on_tool_invocation_failure=True
    )

    # agent.warm_up() # Consider warming up here or in the API startup

    return agent # Return the configured agent instance