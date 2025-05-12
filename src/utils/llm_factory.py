# Method to create LLM instances based on config/choice.
# src/ambitus_ai_models/utils/llm_factory.py
from typing import Any
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiChatGenerator

from haystack.utils import Secret
import os

# Assume API keys are in environment variables
# OPENAI_API_KEY, GOOGLE_API_KEY

def get_llm(llm_choice: str) -> Any:
    """
    Creates and returns a Haystack LLM component based on the choice string.
    
    Returns:
        The appropriate LLM component (OpenAIGenerator or GoogleAIGeminiChatGenerator)
    """
    if llm_choice.lower() == "openai":
        # Ensure API key is available
        api_key = Secret.from_env_var("OPENAI_API_KEY")
        # Use the desired OpenAI model
        return OpenAIGenerator(model="gpt-4o-mini", api_key=api_key)
    elif llm_choice.lower() == "gemini":
         # Ensure API key is available
        api_key = Secret.from_env_var("GOOGLE_API_KEY") # Or GOOGLE_API_KEY, check Gemini component docs
         # Use the desired Gemini model
        return GoogleAIGeminiChatGenerator(model="gemini-1.5-pro-latest", api_key=api_key) # Use latest or specific model
    else:
        # Handle unknown choices (raise an error or return None)
        raise ValueError(f"Unknown LLM choice: {llm_choice}")