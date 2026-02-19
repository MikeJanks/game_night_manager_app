"""Tool aggregation and custom agent tools."""

from typing import List
from sqlmodel import Session
from langchain_core.tools import BaseTool
from api.domains.users.tools import create_user_tools
from api.domains.events.tools import create_user_event_tools, create_channel_event_tools


def create_custom_agent_tools() -> List[BaseTool]:
    """Create custom agent-specific tools.
    
    These are tools that are specific to the agent and not part of
    the domain-specific functionality (users, events).
    
    Returns:
        List of custom agent tools.
    """
    
    return []


def create_user_agent_tools(session: Session) -> List[BaseTool]:
    """Tools for user (session) path: user-scoped event tools."""
    user_tools = create_user_tools(session)
    event_tools = create_user_event_tools(session)
    custom_tools = create_custom_agent_tools()
    return user_tools + event_tools + custom_tools


def create_channel_agent_tools(
    session: Session,
    channel_id: str,
    channel_member_ids: List[str],
    platform: str,
) -> List[BaseTool]:
    """Tools for channel (integration) path: channel-scoped event tools."""
    user_tools = create_user_tools(session)
    event_tools = create_channel_event_tools(session, channel_id, channel_member_ids, platform)
    custom_tools = create_custom_agent_tools()
    return user_tools + event_tools + custom_tools
