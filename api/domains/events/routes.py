from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from typing import Optional

from api.database import SessionDep
from api.domains.auth.dependencies import current_active_user
from api.domains.users.model import User
from api.domains.common.enums import EventStatus, MembershipRole
from .schemas import (
    EventCreate, EventPlanUpdate, EventRead, EventList,
    InviteCreate, InviteResponse,
    MessageCreate, MessageList, MessageRead
)
from . import service as event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Create a new event."""
    event = event_service.create_event(current_user.id, payload, session)
    # Get full event details
    event_data = event_service.get_event_scoped(current_user.id, event.id, session)
    return EventRead(**event_data)


@router.get("", response_model=EventList)
def list_events(
    status_filter: Optional[EventStatus] = Query(None),
    include_cancelled: bool = Query(False),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """List events with scoped visibility."""
    events_data = event_service.list_events_scoped(
        current_user.id,
        status_filter=status_filter,
        include_cancelled=include_cancelled,
        limit=limit,
        offset=offset,
        session=session
    )
    events = [EventRead(**e) for e in events_data]
    return EventList(events=events)


@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Get event details with scoped visibility."""
    event_data = event_service.get_event_scoped(current_user.id, event_id, session)
    return EventRead(**event_data)


@router.patch("/{event_id}", response_model=EventRead)
def update_event_plan(
    event_id: UUID,
    payload: EventPlanUpdate,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Update event plan fields."""
    event = event_service.update_event_plan(current_user.id, event_id, payload, session)
    # Get full event details
    event_data = event_service.get_event_scoped(current_user.id, event_id, session)
    return EventRead(**event_data)


@router.post("/{event_id}/confirm", status_code=status.HTTP_200_OK)
def confirm_event(
    event_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Confirm an event."""
    event_service.set_event_status(current_user.id, event_id, EventStatus.CONFIRMED, session)
    return {"success": True, "message": "Event confirmed"}


@router.post("/{event_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_event(
    event_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Cancel an event."""
    event_service.set_event_status(current_user.id, event_id, EventStatus.CANCELLED, session)
    return {"success": True, "message": "Event cancelled"}


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Delete an event."""
    event_service.delete_event(current_user.id, event_id, session)
    return None


# Invites/Memberships routes

@router.post("/{event_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
def invite_user(
    event_id: UUID,
    payload: InviteCreate,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Invite a user to an event."""
    try:
        event_service.invite_user(
            current_user.id, event_id, payload.invitee_user_id, payload.role, session
        )
        return InviteResponse(success=True, message="User invited")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{event_id}/invites/accept", status_code=status.HTTP_200_OK)
def accept_invite(
    event_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Accept an event invite."""
    try:
        event_service.accept_invite(current_user.id, event_id, session)
        return {"success": True, "message": "Invite accepted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{event_id}/invites/decline", status_code=status.HTTP_200_OK)
def decline_invite(
    event_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Decline an event invite."""
    try:
        event_service.decline_invite(current_user.id, event_id, session)
        return {"success": True, "message": "Invite declined"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{event_id}/plan/confirm", status_code=status.HTTP_200_OK)
def confirm_current_plan(
    event_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Confirm current plan version."""
    try:
        event_service.confirm_current_plan(current_user.id, event_id, session)
        return {"success": True, "message": "Plan confirmed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{event_id}/leave", status_code=status.HTTP_200_OK)
def leave_event(
    event_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Leave an event."""
    try:
        event_service.leave_event(current_user.id, event_id, session)
        return {"success": True, "message": "Left event"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Messages routes

@router.get("/{event_id}/messages", response_model=MessageList)
def list_messages(
    event_id: UUID,
    before: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """List messages for an event."""
    messages_data = event_service.list_messages(
        current_user.id, event_id, before=before, limit=limit, session=session
    )
    messages = [MessageRead(**m) for m in messages_data]
    return MessageList(messages=messages)


@router.post("/{event_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def post_message(
    event_id: UUID,
    payload: MessageCreate,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Post a message to an event."""
    try:
        message = event_service.post_message(current_user.id, event_id, payload.content, session)
        # Get username
        from api.domains.users.model import User
        user = session.get(User, message.user_id)
        username = user.username if user else None
        
        return MessageRead(
            id=message.id,
            event_id=message.event_id,
            user_id=message.user_id,
            username=username,
            content=message.content,
            message_type=message.message_type,
            created_at=message.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
