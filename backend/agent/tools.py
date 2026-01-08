"""Tool aggregation and custom agent tools."""

from typing import List
from uuid import UUID
from sqlmodel import Session
from langchain_core.tools import BaseTool
from domains.users.tools import create_user_tools, create_friend_tools
from domains.games.tools import create_game_tools
from domains.events.tools import create_event_tools


def create_custom_agent_tools() -> List[BaseTool]:
    """Create custom agent-specific tools.
    
    These are tools that are specific to the agent and not part of
    the domain-specific functionality (users, games, events).
    
    Returns:
        List of custom agent tools.
    """
    
    return []


def create_agent_tools(session: Session, current_user_id: UUID) -> List[BaseTool]:
    """Aggregate all tools for the agent.
    
    This function combines:
    1. Domain tools (users, games, events) - bound to the database session
    2. Custom agent tools (calculations, system info, etc.)
    
    Args:
        session: SQLModel database session for domain tools.
        current_user_id: UUID of the current authenticated user.
    
    Returns:
        Complete list of all available tools for the agent.
    """
    # Get domain tools (bound to session)
    user_tools = create_user_tools(session)
    friend_tools = create_friend_tools(session, current_user_id)
    game_tools = create_game_tools(session, current_user_id)
    event_tools = create_event_tools(session, current_user_id)
    
    # Get custom agent tools
    custom_tools = create_custom_agent_tools()
    
    # Combine all tools
    all_tools = user_tools + friend_tools + game_tools + event_tools + custom_tools
    
    return all_tools

