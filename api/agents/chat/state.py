"""LangGraph state definition for the chat agent."""

from typing import Optional
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from .schema import Message

class AgentState(TypedDict):
    messages: Annotated[list[Message], add_messages]
    suggestions: Optional[list[str]]
