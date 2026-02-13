"""Tool aggregation and custom agent tools."""

from typing import List
from sqlmodel import Session
from langchain_core.tools import BaseTool
from api.domains.users.tools import create_user_tools
from api.domains.events.tools import create_event_tools


def create_custom_agent_tools() -> List[BaseTool]:
    """Create custom agent-specific tools.
    
    These are tools that are specific to the agent and not part of
    the domain-specific functionality (users, events).
    
    Returns:
        List of custom agent tools.
    """
    
    return []


def create_agent_tools(session: Session) -> List[BaseTool]:
    """Aggregate all tools for the agent.
    
    This function combines:
    1. Domain tools (users, events) - bound to the database session
    2. Custom agent tools (calculations, system info, etc.)
    
    Args:
        session: SQLModel database session for domain tools.
    
    Returns:
        Complete list of all available tools for the agent.
    """
    user_tools = create_user_tools(session)
    event_tools = create_event_tools(session)
    custom_tools = create_custom_agent_tools()
    return user_tools + event_tools + custom_tools
