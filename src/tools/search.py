# Defines the search tool pipeline(SuperComponent/ComponentTool).
# src/ambitus_ai_models/tools/search.py
from haystack import Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder # Or ChatPromptBuilder
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument, MultiFileConverter
from duckduckgo_api_haystack import DuckduckgoApiWebSearch
from haystack.core.component import Component, Input # Import necessary types
from haystack.core.pipeline import Pipeline
from haystack_experimental.components.embedding_retrievers.search_agent import SuperComponent, ComponentTool # Check correct import path for SuperComponent/ComponentTool
from haystack.core.component import Generator # To potentially pass LLM to tool's internal parts

# Define the function that creates the tool
# It might need the LLM generator if parts of the tool pipeline use an LLM
def create_search_tool(llm: Generator) -> ComponentTool:
    """
    Creates and configures the web search ComponentTool.
    """
    # --- Define the internal search pipeline ---
    search_pipe = Pipeline()
    search_pipe.add_component("search", DuckduckgoApiWebSearch(top_k=10, backend="html"))
    search_pipe.add_component("fetcher", LinkContentFetcher(timeout=3, raise_on_failure=False, retry_attempts=2))
    search_pipe.add_component("converter", MultiFileConverter())
    # Assuming you want to use the LLM passed to this function inside the tool's pipeline
    # You would add the LLM component and connect it.
    search_pipe.add_component("llm_inside_tool", llm) # Add the LLM instance
    # You might also need a prompt builder inside the tool's pipeline
    search_pipe.add_component(
        "prompt_builder",
        PromptBuilder(template="Use these docs to summarize: {% for doc in documents %}{{doc.content}}{% endfor %}")
    )
    # Need a final component that outputs the search results in a useful format
    # The AnswerBuilder from experiment4 might be a good candidate here, used *inside* the tool
    # search_pipe.add_component("answer_formatter", AnswerBuilder()) # Example

    # Connect the pipeline (example connections, adapt to your specific search processing logic inside the tool)
    search_pipe.connect("search.links", "fetcher.urls")
    search_pipe.connect("fetcher.streams", "converter.sources")
    search_pipe.connect("converter.documents", "prompt_builder.documents") # Pass docs to prompt builder
    search_pipe.connect("prompt_builder.prompt", "llm_inside_tool.prompt") # Pass prompt to internal LLM
    # Assume the internal LLM's output is the final result of the pipeline inside the tool
    # You need to figure out the output port name, often 'replies' or 'text'
    # For GoogleAIGeminiChatGenerator, the output port is likely 'replies'


    # --- Wrap the pipeline in a SuperComponent ---
    # Input mapping: Map the 'query' input of the SuperComponent to the 'search' component's 'query' input
    # Output mapping: Map the desired output *from inside the pipeline* to an output port of the SuperComponent
    # If the goal is to get the LLM's response *inside* the tool, map llm_inside_tool.replies
    search_tool_component = SuperComponent(
        pipeline=search_pipe,
        input_mapping={
            "query": ["search.query"],
        },
        output_mapping={
            "llm_inside_tool.replies": "search_result_text" # Map internal LLM output to SuperComponent output
        }
    )

    # --- Wrap the SuperComponent in a ComponentTool ---
    search_tool = ComponentTool(
        name="webSearch",
        description="Use this tool to search for information on the internet. Input format: {query: <search query>}",
        component=search_tool_component # The SuperComponent is the functionality
    )

    return search_tool # Return the created tool

# Similarly, create create_tech_extract_tool() in tech_extract.py