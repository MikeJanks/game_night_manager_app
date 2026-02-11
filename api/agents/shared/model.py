"""Configuration for Groq LLM integration."""

import os
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

def get_groq_llm(
    model: str = "openai/gpt-oss-120b",
    temperature: float = 0.0,
) -> BaseChatModel:
    """Initialize and return a Groq ChatGroq LLM instance."""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name=model,
        temperature=temperature,
    )


def get_default_llm() -> BaseChatModel:
    """Get or create the default LLM instance."""
    return get_groq_llm()
