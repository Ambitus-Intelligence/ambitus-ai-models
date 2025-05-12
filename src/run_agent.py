# run_agent.py
#
# Keep this file in the ROOT directory of your project (ambitus-ai-models/)
# It is a simple script to manually test your agents and tools from the terminal.
#
# To run:
# 1. Make sure your Python environment is activated.
# 2. Make sure your project's dependencies are installed (`pip install -r requirements.txt`).
# 3. You might need to install your local package in editable mode if imports fail:
#    Run `pip install -e .` from the project root directory.
# 4. Set your API keys as environment variables (e.g., OPENAI_API_KEY, GOOGLE_API_KEY).
# 5. Run the script from the project root: `python run_agent.py`

import sys
from haystack.dataclasses import ChatMessage
from haystack.components.builders.answer_builder import AnswerBuilder

# Import your modular code from the src package
try:
    from utils.llm_factory import get_llm
    # Import your agent creation functions
    from agents.researcher import create_researcher_agent
    from agents.tech_extractor import create_tech_extractor_agent
    # Import tool creation functions if agents need them passed explicitly
    from tools.search import create_search_tool
    from tools.tech_extract import create_tech_extractor_tool

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("\nPlease ensure:")
    print("- You are running this script from the project root directory.")
    print("- Your 'src' directory is correctly named and structured.")
    print("- You have installed your local package in editable mode (`pip install -e .`).")
    print("- All dependencies in requirements.txt are installed.")
    sys.exit(1) # Exit if imports fail


def main():
    """
    Runs the selected agent with user-provided inputs.
    """
    print("--- Ambitus AI Models Agent Test Script ---")

    # --- Get User Inputs ---
    available_llms = ["openai", "gemini"]
    available_agents = ["researcher", "tech_extractor"]

    # Get LLM Choice
    while True:
        print("\nAvailable LLMs:", ", ".join(available_llms))
        llm_choice = input("Enter LLM choice: ").strip().lower()
        if llm_choice in available_llms:
            break
        else:
            print(f"Invalid LLM choice. Please choose from: {', '.join(available_llms)}")

    # Get Agent Choice
    while True:
        print("\nAvailable Agents:", ", ".join(available_agents))
        agent_choice = input("Enter Agent choice: ").strip().lower()
        if agent_choice in available_agents:
            break
        else:
            print(f"Invalid Agent choice. Please choose from: {', '.join(available_agents)}")

    # Get Query
    # The query should be structured based on what the agent is designed to process.
    # E.g., "Analyze technologies used by Google in cloud computing?" for tech_extractor agent
    # E.g., "Analyze Zepto's business strategy" for researcher agent
    query = input("\nEnter your query: ").strip()

    # --- Create Components ---
    try:
        # Get the chosen LLM instance
        print(f"\nCreating LLM: {llm_choice}...")
        llm_generator = get_llm(llm_choice)
        print("LLM created.")

        # Create the necessary tools (agents will need specific tools)
        # In a real app, you might manage tool instances more centrally
        # For this test script, we create all tools needed by the agents we might run
        print("Creating tools...")
        search_tool_instance = create_search_tool(llm=llm_generator) # Assuming search tool needs the LLM
        tech_extract_tool_instance = create_tech_extractor_tool() # Assuming tech extractor tool does NOT need the LLM directly
        print("Tools created.")

        # Get the chosen Agent instance
        print(f"Creating Agent: {agent_choice}...")
        agent = None
        tools_for_agent = [] # Define which tools THIS specific agent gets

        if agent_choice == "researcher":
            tools_for_agent = [search_tool_instance] # Researcher needs search tool
            agent = create_researcher_agent(chat_generator=llm_generator, tools=tools_for_agent)
        elif agent_choice == "tech_extractor":
            # Tech extractor agent likely needs BOTH search (to get text) and tech_extract tool
            tools_for_agent = [search_tool_instance, tech_extract_tool_instance]
            agent = create_tech_extractor_agent(chat_generator=llm_generator, tools=tools_for_agent)

        if agent is None:
             print("Error: Failed to create agent instance.")
             sys.exit(1)

        print(f"Agent '{agent_choice}' created with tools: {[tool.name for tool in tools_for_agent]}.")

        # Initialize AnswerBuilder for output formatting
        answer_builder = AnswerBuilder()
        print("AnswerBuilder created.")

    except Exception as e:
        print(f"\nError during component creation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


    # --- Run Agent ---
    print("\nRunning agent...")
    print("-" * 20)
    try:
        # Agents typically take a list of ChatMessage objects as input
        messages = [ChatMessage.from_user(query)]
        agent_output = agent.run(messages=messages)
        print("-" * 20)
        print("Agent finished running.")

        # --- Process and Display Output ---
        # Filter agent's messages to get the final text output(s)
        # Assuming the agent produces ChatMessage objects with text content
        valid_replies = [msg for msg in agent_output["messages"] if getattr(msg, "text", None)]

        if not valid_replies:
            print("\nAgent did not produce a final text response.")
            print("Agent output messages:")
            for msg in agent_output["messages"]:
                print(msg)
            return # Exit function

        # Use AnswerBuilder to format the final replies
        # AnswerBuilder input 'replies' should be a list of ChatMessage objects
        print("\nBuilding final answer...")
        answers = answer_builder.run(query=query, replies=valid_replies)

        # Print the result
        print("\n--- Final Agent Response ---")
        # The structure depends on AnswerBuilder's output, assuming it's a dict with 'answers' list
        if answers and "answers" in answers and answers["answers"]:
             # Assuming Answer objects have a 'data' attribute which is the text
             final_response_text = answers["answers"][-1].data # Get text from the last answer
             print(final_response_text)
        else:
             print("Could not format final answer.")
             print("Raw AnswerBuilder output:", answers)


    except Exception as e:
        print(f"\nError during agent execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()