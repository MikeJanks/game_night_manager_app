"""Pydantic schemas for chat agent API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Tuple, Literal, TypeAlias, Optional


# class Message(BaseModel):
#     """Single message in the conversation."""
#     role: str = Field(..., description="Message role: 'user' or 'assistant'")
#     content: str = Field(..., description="Message content")

Message: TypeAlias = Tuple[Literal["user", "assistant"], str]

class AgentRequest(BaseModel):
    """Input schema for chat requests - accepts full message history as tuples [role, content]."""
    messages: List[Message] = Field(..., description="Complete conversation history as tuples: [['user', 'Hi'], ['assistant', 'Hello']]")


class AgentResponse(BaseModel):
    """Output schema - returns complete message history."""
    messages: List[Message] = Field(..., description="Complete conversation history including new response")
    suggestions: Optional[List[str]] = Field(None, description="List of suggested followup actions")


class Suggestions(BaseModel):
    """Structured output schema for agent suggestions - followup actions or questions for the user."""
    suggestions: List[str] = Field(..., description="List of suggested followup actions or questions for the user")
