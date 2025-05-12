# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal # For type hints
from haystack.dataclasses.chat_message import ChatMessage # Import ChatMessage

# Import your modular code
from src.ambitus_ai_models.utils.llm_factory import get_llm
from src.ambitus_ai_models.tools.search import create_search_tool # Example
from src.ambitus_ai_models.tools.tech_extract import create_tech_extract_tool # Example
from src.ambitus_ai_models.agents.researcher import create_researcher_agent
from src.ambitus_ai_models.agents.tech_extractor import create_tech_extractor_agent
from haystack.components.builders.answer_builder import AnswerBuilder # If AnswerBuilder is used here
from haystack.core.component import Input # Import necessary types if creating components directly

app = FastAPI()

# Update the input model for the API
class QueryInput(BaseModel):
    company_name: str
    agent_choice: Literal["researcher", "tech_extractor"] # Use Literal for allowed string values
    llm_choice: Literal["gemini", "openai"]
    query: str # The actual research/extraction query

# Initialize AnswerBuilder once if it's reusable and stateless
# For stateful components, you might need more sophisticated management
answer_builder = AnswerBuilder()


@app.post("/query")
async def get_agent_response(input_data: QueryInput):
    try:
        # 1. Get the chosen LLM instance
        llm_generator = get_llm(input_data.llm_choice)

        # 2. Create or retrieve the chosen agent instance
        # You'll need to pass the relevant tools and the chosen LLM
        if input_data.agent_choice == "researcher":
            # Create the tools needed by the researcher agent
            search_tool = create_search_tool(llm=llm_generator) # Example: tools might need the LLM
            tools_for_agent = [search_tool]
            # Create the researcher agent
            agent = create_researcher_agent(chat_generator=llm_generator, tools=tools_for_agent)
        elif input_data.agent_choice == "tech_extractor":
            # Create the tools needed by the tech extractor agent
            tech_extract_tool = create_tech_extract_tool(llm=llm_generator) # Example
            tools_for_agent = [tech_extract_tool] # Or maybe both search and tech_extract?
            # Create the tech extractor agent
            agent = create_tech_extractor_agent(chat_generator=llm_generator, tools=tools_for_agent)
        else:
            # This case should not be reached due to Literal type hint, but good practice
             raise HTTPException(status_code=400, detail="Invalid agent choice")

        # You might want to warm_up() the agent here, but consider performance impact on first request
        # agent.warm_up() # Consider if needed and how to manage if it's slow

        # Prepare the initial messages for the agent run
        messages = [ChatMessage.from_user(input_data.query)]

        # Run the agent
        agent_output = agent.run(messages=messages)

        # Filter valid replies (assuming the agent produces ChatMessage objects with text)
        valid_replies = [msg for msg in agent_output["messages"] if getattr(msg, "text", None)]

        # Generate final answers using AnswerBuilder
        # Note: AnswerBuilder expects 'replies' input to be a list of ChatMessage objects
        answers = answer_builder.run(query=input_data.query, replies=valid_replies)


        # Extract the final answer text (adjust based on AnswerBuilder's output structure)
        # Assuming answers["answers"] is a list of Answer objects and you want the text of the last one
        result_text = ""
        if answers and "answers" in answers and answers["answers"]:
             # Assuming Answer objects have a 'data' attribute which is the text
             result_text = answers["answers"][-1].data
        # Or maybe you want the text from all valid_replies? Adjust as needed.


        return JSONResponse(content={"response": result_text})

    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

# Note: The uvicorn running code at the bottom of your sample is for notebooks.
# You run a proper FastAPI app from the terminal using `uvicorn api.main:app --reload`