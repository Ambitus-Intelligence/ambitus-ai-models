# Generic Pipeline Imports
from haystack import Pipeline
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import MultiFileConverter
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from duckduckgo_api_haystack import DuckduckgoApiWebSearch

# Custom Component Imports
from typing import List
from haystack import component, Document

# Custom Component to manage source URLs
@component
class DocumentFormatter:
    """
    Takes a list of Documents and returns two lists of strings:
      - `sources`:  ["Source 1: <url1>", "Source 2: <url2>", …]
      - `information`: ["Information 1: <content1>", …]
    """
    @component.output_types(sources=List[str], information=List[str])
    def run(self, documents: List[Document]):
        sources: List[str] = []
        information: List[str] = []
        for idx, doc in enumerate(documents, start=1):
            url = doc.meta.get("url", "<no-url>")
            sources.append(f"Source {idx}: {url}")
            information.append(f"Information {idx}: {doc.content}")
        return {"sources": sources, "information": information}
    

# Search Pipeline
search_pipe = Pipeline()

search_pipe.add_component("search", DuckduckgoApiWebSearch(top_k=10, backend="auto"))
search_pipe.add_component("fetcher", LinkContentFetcher(timeout=3, raise_on_failure=False, retry_attempts=2))
search_pipe.add_component("converter", MultiFileConverter())
search_pipe.add_component("formatter", DocumentFormatter())

search_pipe.connect("search.links", "fetcher.urls")
search_pipe.connect("fetcher.streams", "converter.sources")
search_pipe.connect("converter.documents", "formatter.documents")

# MCP compliant wrapper function
def search_tool(query: str) -> dict:
    """
    Perform a web search for the given query and return sources and information.
    
    Args:
        query: The search query string
        
    Returns:
        Dict containing 'sources' and 'information' lists
    """
    try:
        # Run the search pipeline
        result = search_pipe.run({"search": {"query": query}})
        
        return {
            "sources": result.get("formatter", {}).get("sources", []),
            "information": result.get("formatter", {}).get("information", []),
            "status": "success"
        }
    except Exception as e:
        return {
            "sources": [],
            "information": [],
            "status": "error",
            "error": str(e)
        }

# Set function metadata for FastMCP
search_tool.__name__ = "search_tool"
search_tool.__doc__ = "Perform a web search and return sources and information lists"