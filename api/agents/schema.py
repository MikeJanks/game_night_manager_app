"""Pydantic schemas for chat agent API requests and responses."""

from typing import Union, Annotated, Optional
from pydantic import BaseModel, Field, Discriminator, model_validator
from langchain_core.messages import HumanMessage, AIMessage


class MessageWithMetadataMixin:
    """Mixin for timestamp injection into message content for LLM context.

    Uses response_metadata['timestamp']. Prepends [timestamp:...] to content.
    Use export_for_response() for API responses (excludes prefix).
    """

    timestamp: str

    @model_validator(mode="after")
    def _inject_timestamp(self):
        self.response_metadata = {**self.response_metadata, "timestamp": self.timestamp}
        self.additional_kwargs = self.additional_kwargs or {}
        if "_original_content" not in self.additional_kwargs:
            self.additional_kwargs["_original_content"] = self.content
            self.content = f"[timestamp:{self.timestamp}] {self.content}"
        if getattr(self, "name", None):
            self.additional_kwargs["name"] = self.name
        return self

    def export_for_response(self) -> str:
        """Content for API response - excludes timestamp prefix."""
        return self.additional_kwargs.get("_original_content", self.content)


class NamedHumanMessage(MessageWithMetadataMixin, HumanMessage):
    """HumanMessage with timestamp injection for LLM context."""
    pass


class NamedAIMessage(MessageWithMetadataMixin, AIMessage):
    """AIMessage with timestamp injection for LLM context."""
    pass


MessageUnion = Annotated[
    Union[NamedHumanMessage, NamedAIMessage],
    Discriminator("type"),
]


class AgentRequest(BaseModel):
    """Input schema for chat requests - accepts full message history as HumanMessage/AIMessage objects."""
    messages: list[MessageUnion] = Field(
        ...,
        description="Complete conversation history. Human: {type: 'human', content: '...', name?: user_id}. AI: {type: 'ai', content: '...'}",
    )
    channel_id: Optional[str] = Field(None, description="Channel id (e.g. Discord channel); required for channel route.")
    channel_member_ids: Optional[list[str]] = Field(
        None,
        description="Discord user IDs in the channel; required for channel route. Used for invite validation only.",
    )


class MessageResponse(BaseModel):
    """Single message in response - symmetric with request format."""
    type: str = Field(..., description="Message type: 'human' or 'ai'")
    content: str = Field(..., description="Message content")
    name: Optional[str] = Field(None, description="User ID for human messages (from message name field)")
    timestamp: Optional[str] = Field(None, description="ISO timestamp when message was sent/received")


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
