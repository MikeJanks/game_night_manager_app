"""Pydantic schemas for chat agent API requests and responses."""

from typing import Union, Annotated, Optional
from pydantic import BaseModel, Field, Discriminator, model_validator
from langchain_core.messages import HumanMessage, AIMessage


class NamedHumanMessage(HumanMessage):
    """HumanMessage that syncs name into additional_kwargs for Groq API compatibility.

    langchain_groq only includes the name field when it's in additional_kwargs,
    so we ensure it's set here for messages with a name.
    """

    @model_validator(mode="after")
    def _sync_name_to_additional_kwargs(self) -> "NamedHumanMessage":
        if self.name:
            self.additional_kwargs = {**self.additional_kwargs, "name": self.name}
        return self


MessageUnion = Annotated[
    Union[NamedHumanMessage, AIMessage],
    Discriminator("type"),
]


class AgentRequest(BaseModel):
    """Input schema for chat requests - accepts full message history as HumanMessage/AIMessage objects."""
    messages: list[MessageUnion] = Field(
        ...,
        description="Complete conversation history. Human: {type: 'human', content: '...', name?: user_id}. AI: {type: 'ai', content: '...'}",
    )


class MessageResponse(BaseModel):
    """Single message in response - symmetric with request format."""
    type: str = Field(..., description="Message type: 'human' or 'ai'")
    content: str = Field(..., description="Message content")
    name: Optional[str] = Field(None, description="User ID for human messages (from message name field)")


class AgentResponse(BaseModel):
    """Output schema - returns complete message history in same format as request."""
    messages: list[MessageResponse] = Field(
        ...,
        description="Complete conversation history including new response",
    )
    suggestions: Optional[list[str]] = Field(None, description="List of suggested followup actions")


class Suggestions(BaseModel):
    """Structured output schema for agent suggestions - followup actions or questions for the user."""
    suggestions: list[str] = Field(..., description="List of suggested followup actions or questions for the user")
