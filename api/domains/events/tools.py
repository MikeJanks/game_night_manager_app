from typing import Dict, Any, Optional
from langchain_core.tools import tool
from sqlmodel import Session
from uuid import UUID

from . import service as event_service
from .schemas import EventCreate, EventPlanUpdate, InviteCreate
from api.domains.common.enums import EventStatus, MembershipRole


def create_event_tools(session: Session):
    """Create event-related tools bound to a database session."""
    
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
        event = event_service.create_event(actor_id, payload, session)
        event_data = event_service.get_event_scoped(actor_id, event.id, session)
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
            event_data = event_service.get_event_scoped(actor_id, UUID(event_id), session)
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
        events_data = event_service.list_events_scoped(
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
        events_data = event_service.list_events_scoped(
            actor_id,
            status_filter=status_enum,
            include_cancelled=include_cancelled,
            user_only=True,
            limit=limit,
            offset=offset,
            session=session
        )
        return {"events": events_data}
    
    @tool
    def update_event_plan(user_id: str, event_id: str, event_plan_update: EventPlanUpdate) -> Dict[str, Any]:
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
        Only include the fields you want to change in event_plan_update - omitted fields remain unchanged.
        """
        actor_id = UUID(user_id)
        event = event_service.update_event_plan(actor_id, UUID(event_id), event_plan_update, session)
        event_data = event_service.get_event_scoped(actor_id, event.id, session)
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
            event_service.set_event_status(actor_id, UUID(event_id), EventStatus.CONFIRMED, session)
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
            event_service.set_event_status(actor_id, UUID(event_id), EventStatus.CANCELLED, session)
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
            event_service.delete_event(actor_id, UUID(event_id), session)
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
            event_service.invite_user(
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
            event_service.accept_invite(actor_id, UUID(event_id), session)
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
            event_service.decline_invite(actor_id, UUID(event_id), session)
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
            event_service.leave_event(actor_id, UUID(event_id), session)
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
