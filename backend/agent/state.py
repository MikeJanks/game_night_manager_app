"""LangGraph state definition for the agent."""

from typing import Optional
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from .schema import Message

class AgentState(TypedDict):
    messages: Annotated[list[Message], add_messages]
    suggestions: Optional[list[str]]