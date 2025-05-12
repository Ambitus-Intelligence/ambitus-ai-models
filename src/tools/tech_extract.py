# Defines the tech extraction tool pipeline.
# src/ambitus_ai_models/tools/tech_extract.py

# Import necessary libraries for the core logic
import os
import spacy
from keybert import KeyBERT
from collections import defaultdict

# Import necessary Haystack components for the Tool wrapper
# Note: This uses the Tool from haystack.tools, which is different from
# the ComponentTool used for the search tool (which wraps Haystack components).
# We will discuss this difference next.
from haystack.tools import Tool

# --- Core Tech Extraction Logic ---
# This class contains the actual steps for text cleaning, keyword extraction, categorization, etc.
class AutonomousTechExtractorAgent: # Consider renaming this class just 'TechExtractorLogic' or similar
                                   # to avoid confusion with the Haystack Agent class later
    """
    Core logic for extracting and categorizing technology terms from text.
    """
    def __init__(self):
        """Initializes the TechExtractorLogic with spaCy and KeyBERT models."""
        try:
            # Suppress potential Torch compile debug messages if not needed
            os.environ["TORCH_COMPILE_DEBUG"] = "0" # Corrected from 1 to 0 to disable debug
            os.environ["TORCH_COMPILE"] = "0"

            # Load necessary models
            # Consider handling potential errors if models are not downloaded
            self.spacy_nlp = spacy.load("en_core_web_sm")
            self.kw_model = KeyBERT(model='paraphrase-MiniLM-L6-v2')

            # Define tech categories - Could potentially load this from a config file later
            self.tech_categories = {
                "Operations": ["ai", "data analytics", "predictive", "optimization", "forecasting", "automation", "bot"],
                "Customer Experience": ["membership", "personalized", "behavior analytics", "recommendation"],
                "Supply Chain": ["inventory", "tracking", "logistics", "delivery"],
                "Sustainability": ["eco", "green", "environment", "carbon", "sustainability"]
            }
            print("AutonomousTechExtractorAgent initialized.") # Optional: for debugging initialization

        except Exception as e:
            print(f"Error loading libraries for AutonomousTechExtractorAgent: {e}")
            # Consider raising the exception or having a way to check if initialization failed
            self.initialized = False # Add a flag to check if models loaded
            # raise # Uncomment to stop execution if models fail to load
        else:
            self.initialized = True # Set flag if successful

    def clean_text(self, text: str) -> str:
        """Cleans text by joining sentences longer than a minimum length."""
        if not self.initialized: raise RuntimeError("TechExtractorAgent not initialized.") # Check if models loaded
        doc = self.spacy_nlp(text)
        # Keep sentences with more than 20 non-whitespace characters
        return " ".join([sent.text.strip() for sent in doc.sents if len(sent.text.strip().replace(" ", "")) > 20])

    def extract_keywords(self, text: str, top_n: int = 15) -> list[tuple[str, float]]:
        """Extracts keywords from text using KeyBERT."""
        if not self.initialized: raise RuntimeError("TechExtractorAgent not initialized.")
        if not text: return []
        try:
             return self.kw_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 3),
                stop_words="english",
                use_maxsum=True,
                top_n=top_n
            )
        except Exception as e:
             print(f"Error during keyword extraction: {e}")
             return []


    def categorize_keywords(self, keywords: list[tuple[str, float]]) -> tuple[dict[str, list[str]], list[str]]:
        """Categorizes extracted keywords based on predefined categories."""
        categorized = defaultdict(list)
        tech_terms = []

        for phrase, _ in keywords:
            phrase_lower = phrase.lower()
            tech_terms.append(phrase)
            for category, terms_list in self.tech_categories.items():
                if any(term in phrase_lower for term in terms_list):
                    categorized[category].append(phrase)
                    break # Assign to the first matching category

        return dict(categorized), tech_terms # Return as a standard dict

    def find_relationships(self, text: str, tech_terms: list[str]) -> list[dict]:
        """Finds sentences containing multiple tech terms to identify relationships."""
        relationships = []
        if not text or not tech_terms or len(tech_terms) < 2: return [] # Need at least 2 terms to find relationship in a sentence

        # Process text sentence by sentence (assuming sentences end with .)
        # A more robust approach might use spacy's sentence segmentation
        for sent in text.split('.'):
             # Simple check if sentence contains at least two *different* tech terms
            matched = [term for term in tech_terms if term.lower() in sent.lower()]
            if len(set(matched)) >= 2: # Use set to count unique terms matched
                relationships.append({
                    "technologies": list(set(matched)), # Store unique matched terms
                    "context": sent.strip() + "." # Add back the potential period
                })
        return relationships

    def summarize(self, categorized: dict[str, list[str]]) -> dict:
        """Provides summary metrics for the extraction."""
        total = sum(len(v) for v in categorized.values())
        return {
            "Total Technologies": total,
            "Categories Covered": f"{len(categorized)}/{len(self.tech_categories)}"
        }

    def run(self, text: str) -> dict:
        """
        Runs the full tech extraction process on the input text.

        Args:
            text: The input text document.

        Returns:
            A dictionary containing categorized technologies, relationships, and summary.
        """
        if not self.initialized:
             print("Extraction skipped: AutonomousTechExtractorAgent not initialized.")
             return {
                "Technologies by Category": {},
                "Technology Relationships": [],
                "Summary Metrics": {"Total Technologies": 0, "Categories Covered": "0/?"}
            }

        # Ensure text is a string
        if not isinstance(text, str):
             print(f"Warning: Expected string input, but received {type(text)}. Skipping extraction.")
             return {
                "Technologies by Category": {},
                "Technology Relationships": [],
                "Summary Metrics": {"Total Technologies": 0, "Categories Covered": "0/?"}
            }


        cleaned = self.clean_text(text)
        keywords = self.extract_keywords(cleaned)
        categorized, tech_terms = self.categorize_keywords(keywords)
        # Note: Relationships are found in the *cleaned* text, not the original
        relationships = self.find_relationships(cleaned, tech_terms)
        summary = self.summarize(categorized)

        return {
            "Technologies by Category": categorized, # Use the dict directly
            "Technology Relationships": relationships,
            "Summary Metrics": summary
        }

# --- Haystack Tool Definition ---
# This function creates and returns the ComponentTool that wraps the tech extraction logic.
# We'll use the ComponentTool pattern for consistency with the search tool.
# The tech extraction logic needs to be wrapped as a Haystack Component first if
# we want to use SuperComponent/ComponentTool in the standard v2 way.

# Let's adapt the AutonomousTechExtractorAgent to be a Haystack Component
from haystack.core.component import Component, Input, Output, decorate_component

# @Component # Use this decorator if this was a standalone component, but we'll instantiate
# Need to make the run method compatible with Haystack Component inputs/outputs

# Let's define a simple Component wrapper for the Tech Extraction Logic
# This is required to use SuperComponent or ComponentTool in the standard v2 way
# that you used for the search tool.

@decorate_component(
    inputs={
        "text": Input(type=str, description="The text document to extract technologies from.")
    },
    outputs={
        "extraction_result": Output(type=dict, description="The extracted technologies, relationships, and summary.")
    }
)
class TechExtractionComponent:
    """
    A Haystack component that performs technology extraction using the core logic.
    """
    def __init__(self):
        """Initializes the TechExtractionComponent and the core logic."""
        # Initialize the core logic class
        self.extractor_logic = AutonomousTechExtractorAgent() # Using the logic class defined above

    # The run method must match the decorated inputs/outputs
    def run(self, text: str): # Input matches "text"
        """Runs the tech extraction logic."""
        if not self.extractor_logic.initialized:
             # Return a placeholder or raise an error if initialization failed
             return {"extraction_result": {}} # Output matches "extraction_result"

        result = self.extractor_logic.run(text=text)
        return {"extraction_result": result} # Output matches "extraction_result"


# Now create the ComponentTool wrapping this new Haystack Component
from haystack_experimental.components.embedding_retrievers.search_agent import ComponentTool # Check this import path again if needed


def create_tech_extractor_tool() -> ComponentTool:
    """
    Creates and configures the Tech Extractor ComponentTool.
    """
    # Instantiate the Haystack Component wrapper
    tech_extraction_component_instance = TechExtractionComponent()

    # Wrap the component in a ComponentTool
    tech_extractor_tool_instance = ComponentTool(
        name="TechExtractorTool", # Name the agent will use
        description="Extracts and categorizes technology and novel terms from a document. Input format: {text: <document text>}", # Description for the agent
        component=tech_extraction_component_instance # The component providing the functionality
    )

    return tech_extractor_tool_instance

# Note: The code below this point in the original notebook is for demonstration
# and should NOT be included in this file.
# --- Demonstration code from original notebook (exclude) ---
# tech_extractor = AutonomousTechExtractorAgent()
# tech_extractor_tool = Tool(...) # This old style tool creation is not used now
# input_text = input(...)
# result = tech_extractor_tool.invoke(text=input_text)
# print(...)
# --- End of Demonstration code ---