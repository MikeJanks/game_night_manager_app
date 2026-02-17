from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
from sqlmodel import Session
from uuid import UUID

from . import service as event_service
from .service import ResolvedActor
from .schemas import EventCreate, EventPlanUpdate
from api.domains.common.enums import EventStatus, MembershipRole, ExternalSource


def _resolve_actor(identifier: str, is_channel_path: bool) -> ResolvedActor:
    """Resolve message 'name' to ResolvedActor. User path: UUID only. Channel path: UUID or Discord id."""
    if not identifier:
        raise ValueError("user_id is required")
    # Try UUID first (app user)
    try:
        return ResolvedActor(user_id=UUID(identifier), external_source=None, external_id=None)
    except (ValueError, TypeError):
        pass
    if not is_channel_path:
        raise ValueError("user_id must be a valid UUID for this context")
    # Channel path: Discord id as discord:snowflake or bare snowflake
    if identifier.startswith("discord:"):
        snowflake = identifier[8:].strip()
        if snowflake.isdigit():
            return ResolvedActor(user_id=None, external_source=ExternalSource.DISCORD, external_id=snowflake)
    if identifier.isdigit():
        return ResolvedActor(user_id=None, external_source=ExternalSource.DISCORD, external_id=identifier)
    raise ValueError("user_id must be a valid UUID or Discord id (e.g. discord:123 or 123)")


def create_user_event_tools(session: Session) -> List:
    """Create event tools for the user (session) path. Actor is app user UUID only."""
    
    @tool
    def create_event(user_id: str, game_name: str, event_name: str) -> Dict[str, Any]:
        """Create a new event.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            game_name: The name of the game for this event
            event_name: The name of the event
        
        Returns a dict with an 'event' key containing the created event.
        """
        actor_id = UUID(user_id)
        payload = EventCreate(game_name=game_name, event_name=event_name)
        event = event_service.create_event_for_user(actor_id, payload, session)
        event_data = event_service.get_event_for_user(actor_id, event.id, session)
        return {"event": event_data}
    
    @tool
    def get_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Get event details.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
        
        Returns a dict with an 'event' key containing the event details.
        """
        try:
            actor_id = UUID(user_id)
            event_data = event_service.get_event_for_user(actor_id, UUID(event_id), session)
            return {"event": event_data}
        except Exception as e:
            return {"event": None, "error": str(e)}
    
    @tool
    def list_events(
        user_id: str,
        status_filter: Optional[str] = None,
        include_cancelled: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List events with scoped visibility.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            status_filter: Optional status filter (PLANNING, CONFIRMED, CANCELLED)
            include_cancelled: Whether to include cancelled events (default: False)
            limit: Maximum number of events to return (default: 100)
            offset: Number of events to skip (default: 0)
        
        Returns a dict with an 'events' key containing a list of events.
        """
        status_enum = None
        if status_filter:
            try:
                status_enum = EventStatus[status_filter.upper()]
            except KeyError:
                pass
        actor_id = UUID(user_id)
        events_data = event_service.list_events_for_user(
            actor_id,
            status_filter=status_enum,
            include_cancelled=include_cancelled,
            limit=limit,
            offset=offset,
            session=session
        )
        return {"events": events_data}
    
    @tool
    def get_user_events(
        user_id: str,
        status_filter: Optional[str] = None,
        include_cancelled: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get all events where the specified user is a member.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            status_filter: Optional status filter (PLANNING, CONFIRMED, CANCELLED)
            include_cancelled: Whether to include cancelled events (default: False)
            limit: Maximum number of events to return (default: 100)
            offset: Number of events to skip (default: 0)
        
        Returns a dict with an 'events' key containing a list of events.
        """
        status_enum = None
        if status_filter:
            try:
                status_enum = EventStatus[status_filter.upper()]
            except KeyError:
                pass
        actor_id = UUID(user_id)
        events_data = event_service.list_events_for_user(
            actor_id,
            status_filter=status_enum,
            include_cancelled=include_cancelled,
            limit=limit,
            offset=offset,
            session=session
        )
        return {"events": events_data}
    
    @tool
    def update_event_plan(user_id: str, event_id: str, event_plan_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update event plan fields.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
            event_plan_update: Object containing only the fields to update. Omit any field to leave it unchanged.
                - event_datetime: Optional new event datetime (ISO format string, e.g. 2025-02-15T19:00:00)
                - location_or_link: Optional new location or link
                - event_name: Optional new event name
        
        Returns a dict with an 'event' key containing the updated event.
        """
        actor_id = UUID(user_id)
        payload = EventPlanUpdate(**(event_plan_update or {}))
        event = event_service.update_event_plan_for_user(actor_id, UUID(event_id), payload, session)
        event_data = event_service.get_event_for_user(actor_id, event.id, session)
        return {"event": event_data}
    
    @tool
    def confirm_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Confirm an event.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
        
        Returns a dict with success status.
        """
        try:
            actor_id = UUID(user_id)
            event_service.set_event_status_for_user(actor_id, UUID(event_id), EventStatus.CONFIRMED, session)
            return {"success": True, "message": "Event confirmed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def cancel_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Cancel an event.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
        
        Returns a dict with success status.
        """
        try:
            actor_id = UUID(user_id)
            event_service.set_event_status_for_user(actor_id, UUID(event_id), EventStatus.CANCELLED, session)
            return {"success": True, "message": "Event cancelled"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def delete_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Delete an event.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
        
        Returns a dict with success status.
        """
        try:
            actor_id = UUID(user_id)
            event_service.delete_event_for_user(actor_id, UUID(event_id), session)
            return {"success": True, "message": "Event deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def invite_user(user_id: str, event_id: str, invitee_user_id: str, role: str) -> Dict[str, Any]:
        """Invite a user to an event.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
            invitee_user_id: The UUID of the user to invite
            role: The role (HOST or ATTENDEE)
        
        Returns a dict with success status.
        """
        try:
            actor_id = UUID(user_id)
            role_enum = MembershipRole[role.upper()]
            event_service.invite_user_for_user(
                actor_id, UUID(event_id), UUID(invitee_user_id), role_enum, session
            )
            return {"success": True, "message": "User invited"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def accept_invite(user_id: str, event_id: str) -> Dict[str, Any]:
        """Accept an event invite.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
        
        Returns a dict with success status.
        """
        try:
            actor_id = UUID(user_id)
            event_service.accept_invite_for_user(actor_id, UUID(event_id), session)
            return {"success": True, "message": "Invite accepted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def decline_invite(user_id: str, event_id: str) -> Dict[str, Any]:
        """Decline an event invite.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
        
        Returns a dict with success status.
        """
        try:
            actor_id = UUID(user_id)
            event_service.decline_invite_for_user(actor_id, UUID(event_id), session)
            return {"success": True, "message": "Invite declined"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def leave_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Leave an event.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user performing the action (from the message's name field).
            event_id: The UUID of the event
        
        Returns a dict with success status.
        """
        try:
            actor_id = UUID(user_id)
            event_service.leave_event_for_user(actor_id, UUID(event_id), session)
            return {"success": True, "message": "Left event"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return [
        create_event,
        get_event,
        list_events,
        get_user_events,
        update_event_plan,
        confirm_event,
        cancel_event,
        delete_event,
        invite_user,
        accept_invite,
        decline_invite,
        leave_event,
    ]


def create_channel_event_tools(
    session: Session,
    channel_id: str,
    channel_member_ids: List[str],
) -> List:
    """Create event tools for the channel (integration) path. Tools are scoped to channel_id; invitee must be in channel_member_ids."""
    
    bound_channel_id = channel_id
    bound_member_ids = list(channel_member_ids) if channel_member_ids else []
    
    @tool
    def create_event(user_id: str, game_name: str, event_name: str) -> Dict[str, Any]:
        """Create a new event in this channel.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The identifier of the user performing the action (from the message's name field; UUID or Discord id).
            game_name: The name of the game for this event
            event_name: The name of the event
        
        Returns a dict with an 'event' key containing the created event.
        """
        actor = _resolve_actor(user_id, is_channel_path=True)
        payload = EventCreate(game_name=game_name, event_name=event_name)
        event = event_service.create_event_in_channel(actor, payload, bound_channel_id, session)
        event_data = event_service.get_event_in_channel(event.id, bound_channel_id, session)
        return {"event": event_data}
    
    @tool
    def get_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Get event details (for an event in this channel).
        
        Args:
            user_id: The identifier of the user performing the action (from the message's name field).
            event_id: The UUID of the event
        
        Returns a dict with an 'event' key containing the event details.
        """
        try:
            event_data = event_service.get_event_in_channel(UUID(event_id), bound_channel_id, session)
            return {"event": event_data}
        except Exception as e:
            return {"event": None, "error": str(e)}
    
    @tool
    def list_events(
        user_id: str,
        status_filter: Optional[str] = None,
        include_cancelled: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List all events in this channel.
        
        Args:
            user_id: The identifier of the user performing the action (from the message's name field).
            status_filter: Optional status filter (PLANNING, CONFIRMED, CANCELLED)
            include_cancelled: Whether to include cancelled events (default: False)
            limit: Maximum number of events to return (default: 100)
            offset: Number of events to skip (default: 0)
        
        Returns a dict with an 'events' key containing a list of events.
        """
        status_enum = None
        if status_filter:
            try:
                status_enum = EventStatus[status_filter.upper()]
            except KeyError:
                pass
        events_data = event_service.list_events_for_channel(
            bound_channel_id,
            status_filter=status_enum,
            include_cancelled=include_cancelled,
            limit=limit,
            offset=offset,
            session=session
        )
        return {"events": events_data}
    
    @tool
    def get_user_events(
        user_id: str,
        status_filter: Optional[str] = None,
        include_cancelled: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get all events in this channel (same as list_events for channel context).
        
        Args:
            user_id: The identifier of the user performing the action (from the message's name field).
            status_filter: Optional status filter (PLANNING, CONFIRMED, CANCELLED)
            include_cancelled: Whether to include cancelled events (default: False)
            limit: Maximum number of events to return (default: 100)
            offset: Number of events to skip (default: 0)
        
        Returns a dict with an 'events' key containing a list of events.
        """
        status_enum = None
        if status_filter:
            try:
                status_enum = EventStatus[status_filter.upper()]
            except KeyError:
                pass
        events_data = event_service.list_events_for_channel(
            bound_channel_id,
            status_filter=status_enum,
            include_cancelled=include_cancelled,
            limit=limit,
            offset=offset,
            session=session
        )
        return {"events": events_data}
    
    @tool
    def update_event_plan(user_id: str, event_id: str, event_plan_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update event plan fields (host only, event must be in this channel).
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The identifier of the user performing the action (from the message's name field).
            event_id: The UUID of the event
            event_plan_update: Object containing only the fields to update.
        
        Returns a dict with an 'event' key containing the updated event.
        """
        actor = _resolve_actor(user_id, is_channel_path=True)
        payload = EventPlanUpdate(**(event_plan_update or {}))
        event = event_service.update_event_plan_in_channel(
            actor, UUID(event_id), bound_channel_id, payload, session
        )
        event_data = event_service.get_event_in_channel(event.id, bound_channel_id, session)
        return {"event": event_data}
    
    @tool
    def confirm_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Confirm an event (host only, event must be in this channel)."""
        try:
            actor = _resolve_actor(user_id, is_channel_path=True)
            event_service.set_event_status_in_channel(
                actor, UUID(event_id), bound_channel_id, EventStatus.CONFIRMED, session
            )
            return {"success": True, "message": "Event confirmed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def cancel_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Cancel an event (host only, event must be in this channel)."""
        try:
            actor = _resolve_actor(user_id, is_channel_path=True)
            event_service.set_event_status_in_channel(
                actor, UUID(event_id), bound_channel_id, EventStatus.CANCELLED, session
            )
            return {"success": True, "message": "Event cancelled"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def delete_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Delete an event (host only, event must be in this channel)."""
        try:
            actor = _resolve_actor(user_id, is_channel_path=True)
            event_service.delete_event_in_channel(actor, UUID(event_id), bound_channel_id, session)
            return {"success": True, "message": "Event deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def invite_user(user_id: str, event_id: str, invitee_user_id: str, role: str) -> Dict[str, Any]:
        """Invite a user to an event (channel context: invitee_user_id is the Discord user id; invitee must be in this channel).
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The identifier of the user performing the action (from the message's name field).
            event_id: The UUID of the event
            invitee_user_id: The Discord user id of the user to invite (must be in this channel)
            role: The role (HOST or ATTENDEE)
        
        Returns a dict with success status.
        """
        try:
            actor = _resolve_actor(user_id, is_channel_path=True)
            role_enum = MembershipRole[role.upper()]
            event_service.invite_user_in_channel(
                actor, UUID(event_id), bound_channel_id, invitee_user_id, role_enum, bound_member_ids, session
            )
            return {"success": True, "message": "User invited"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def accept_invite(user_id: str, event_id: str) -> Dict[str, Any]:
        """Accept an event invite (event must be in this channel)."""
        try:
            actor = _resolve_actor(user_id, is_channel_path=True)
            event_service.accept_invite_in_channel(actor, UUID(event_id), bound_channel_id, session)
            return {"success": True, "message": "Invite accepted"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def decline_invite(user_id: str, event_id: str) -> Dict[str, Any]:
        """Decline an event invite (event must be in this channel)."""
        try:
            actor = _resolve_actor(user_id, is_channel_path=True)
            event_service.decline_invite_in_channel(actor, UUID(event_id), bound_channel_id, session)
            return {"success": True, "message": "Invite declined"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def leave_event(user_id: str, event_id: str) -> Dict[str, Any]:
        """Leave an event (event must be in this channel)."""
        try:
            actor = _resolve_actor(user_id, is_channel_path=True)
            event_service.leave_event_in_channel(actor, UUID(event_id), bound_channel_id, session)
            return {"success": True, "message": "Left event"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return [
        create_event,
        get_event,
        list_events,
        get_user_events,
        update_event_plan,
        confirm_event,
        cancel_event,
        delete_event,
        invite_user,
        accept_invite,
        decline_invite,
        leave_event,
    ]


def create_event_tools(session: Session) -> List:
    """Create event tools for the user (session) path. Kept for backward compatibility; prefer create_user_event_tools."""
    return create_user_event_tools(session)
