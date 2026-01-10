from typing import List, Optional
from sqlmodel import Session, select, func, or_, and_
from sqlalchemy import update
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone
from .model import Event, EventMembership, EventMessage
from .schemas import (
    EventCreate, EventPlanUpdate, EventRead, EventMembershipRead
)
from backend.domains.users.model import User, Friendship
from backend.domains.games.model import Game
from backend.domains.common.enums import EventStatus, MembershipRole, MembershipStatus, MessageType, FriendshipStatus


# Event service functions

def create_event(current_user_id: UUID, payload: EventCreate, session: Session) -> Event:
    """Create a new event with creator as HOST."""
    # Verify game exists
    game = session.get(Game, payload.game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Create event
    event = Event(
        game_id=payload.game_id,
        event_name=payload.event_name,
        status=EventStatus.PLANNING,
        plan_version=1,
        plan_updated_at=datetime.now(timezone.utc)
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    
    # Create membership for creator as HOST
    membership = EventMembership(
        event_id=event.id,
        user_id=current_user_id,
        role=MembershipRole.HOST,
        status=MembershipStatus.ACCEPTED
    )
    session.add(membership)
    session.commit()
    
    return event


def get_event_scoped(current_user_id: UUID, event_id: UUID, session: Session) -> dict:
    """Get event with scoped visibility and membership info."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check visibility: user is member OR friend is ACCEPTED member
    user_membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id
        )
    ).first()
    
    visible = False
    if user_membership and user_membership.status in [MembershipStatus.PENDING, MembershipStatus.ACCEPTED]:
        visible = True
    else:
        # Check if any ACCEPTED friend is an ACCEPTED member
        # Get all ACCEPTED friends
        friendships = session.exec(
            select(Friendship).where(
                Friendship.status == FriendshipStatus.ACCEPTED,
                or_(
                    Friendship.user_id == current_user_id,
                    Friendship.friend_user_id == current_user_id
                )
            )
        ).all()
        
        friend_ids = set()
        for f in friendships:
            if f.user_id == current_user_id:
                friend_ids.add(f.friend_user_id)
            else:
                friend_ids.add(f.user_id)
        
        # Check if any friend is an ACCEPTED member
        if friend_ids:
            friend_membership = session.exec(
                select(EventMembership).where(
                    EventMembership.event_id == event_id,
                    EventMembership.user_id.in_(friend_ids),
                    EventMembership.status == MembershipStatus.ACCEPTED
                )
            ).first()
            
            if friend_membership:
                visible = True
    
    if not visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get my membership
    my_membership = None
    if user_membership:
        my_membership = EventMembershipRead(
            role=user_membership.role,
            status=user_membership.status,
            confirmed_plan_version=user_membership.confirmed_plan_version
        )
    
    # Calculate is_confirmed_for_plan
    is_confirmed_for_plan = (
        my_membership is not None
        and my_membership.status == MembershipStatus.ACCEPTED
        and my_membership.confirmed_plan_version == event.plan_version
    )
    
    # Fetch game name
    game = session.get(Game, event.game_id)
    game_name = game.name if game else None
    
    # Fetch all memberships with user data
    all_memberships = session.exec(
        select(EventMembership).where(EventMembership.event_id == event_id)
    ).all()
    
    # Batch fetch users
    user_ids = [m.user_id for m in all_memberships]
    users = {}
    if user_ids:
        users_list = session.exec(select(User).where(User.id.in_(user_ids))).all()
        users = {user.id: user for user in users_list}
    
    # Group memberships by role
    hosts = []
    attendees = []
    
    for membership in all_memberships:
        user = users.get(membership.user_id)
        if not user:
            continue
        
        member_data = {
            "user_id": membership.user_id,
            "username": user.username,
            "status": membership.status
        }
        
        if membership.role == MembershipRole.HOST:
            hosts.append(member_data)
        elif membership.role == MembershipRole.ATTENDEE:
            attendees.append(member_data)
    
    return {
        "id": event.id,
        "game_id": event.game_id,
        "game_name": game_name,
        "event_name": event.event_name,
        "event_datetime": event.event_datetime,
        "location_or_link": event.location_or_link,
        "status": event.status,
        "plan_version": event.plan_version,
        "plan_updated_at": event.plan_updated_at,
        "my_membership": my_membership,
        "is_confirmed_for_plan": is_confirmed_for_plan,
        "hosts": hosts,
        "attendees": attendees
    }


def list_events_scoped(
    current_user_id: UUID,
    status_filter: Optional[EventStatus] = None,
    include_cancelled: bool = False,
    user_only: bool = False,
    limit: int = 100,
    offset: int = 0,
    session: Session = None
) -> List[dict]:
    """List events with scoped visibility."""
    if session is None:
        raise ValueError("Session is required")
    
    # Get events where user is member
    user_event_ids = session.exec(
        select(EventMembership.event_id).where(
            EventMembership.user_id == current_user_id,
            EventMembership.status.in_([MembershipStatus.PENDING, MembershipStatus.ACCEPTED])
        )
    ).all()
    
    # Get events where ACCEPTED friend is ACCEPTED member (only if not user_only)
    visible_event_ids = set(user_event_ids)
    
    if not user_only:
        # First get all ACCEPTED friends
        friendships = session.exec(
            select(Friendship).where(
                Friendship.status == FriendshipStatus.ACCEPTED,
                or_(
                    Friendship.user_id == current_user_id,
                    Friendship.friend_user_id == current_user_id
                )
            )
        ).all()
        
        friend_ids = set()
        for f in friendships:
            if f.user_id == current_user_id:
                friend_ids.add(f.friend_user_id)
            else:
                friend_ids.add(f.user_id)
        
        # Get events where friends are ACCEPTED members
        friend_event_ids = []
        if friend_ids:
            friend_event_ids = session.exec(
                select(EventMembership.event_id).where(
                    EventMembership.user_id.in_(friend_ids),
                    EventMembership.status == MembershipStatus.ACCEPTED
                ).distinct()
            ).all()
        
        # Combine event IDs
        visible_event_ids = visible_event_ids | set(friend_event_ids)
    
    if not visible_event_ids:
        return []
    
    # Build query
    statement = select(Event).where(Event.id.in_(visible_event_ids))
    
    # Filter by status
    if status_filter:
        statement = statement.where(Event.status == status_filter)
    
    # Exclude cancelled by default
    if not include_cancelled:
        statement = statement.where(Event.status != EventStatus.CANCELLED)
    
    statement = statement.offset(offset).limit(limit)
    events = session.exec(statement).all()
    
    # Batch fetch games
    game_ids = {event.game_id for event in events}
    game_name_map = {}
    if game_ids:
        games = session.exec(select(Game).where(Game.id.in_(game_ids))).all()
        game_name_map = {game.id: game.name for game in games}
    
    # Build response with membership info for each
    result = []
    for event in events:
        user_membership = session.exec(
            select(EventMembership).where(
                EventMembership.event_id == event.id,
                EventMembership.user_id == current_user_id
            )
        ).first()
        
        my_membership = None
        if user_membership:
            my_membership = EventMembershipRead(
                role=user_membership.role,
                status=user_membership.status,
                confirmed_plan_version=user_membership.confirmed_plan_version
            )
        
        is_confirmed_for_plan = (
            my_membership is not None
            and my_membership.status == MembershipStatus.ACCEPTED
            and my_membership.confirmed_plan_version == event.plan_version
        )
        
        # Get game name
        game_name = game_name_map.get(event.game_id)
        
        # Fetch all memberships with user data
        all_memberships = session.exec(
            select(EventMembership).where(EventMembership.event_id == event.id)
        ).all()
        
        # Batch fetch users for this event
        user_ids = [m.user_id for m in all_memberships]
        users = {}
        if user_ids:
            users_list = session.exec(select(User).where(User.id.in_(user_ids))).all()
            users = {user.id: user for user in users_list}
        
        # Group memberships by role
        hosts = []
        attendees = []
        
        for membership in all_memberships:
            user = users.get(membership.user_id)
            if not user:
                continue
            
            member_data = {
                "user_id": membership.user_id,
                "username": user.username,
                "status": membership.status
            }
            
            if membership.role == MembershipRole.HOST:
                hosts.append(member_data)
            elif membership.role == MembershipRole.ATTENDEE:
                attendees.append(member_data)
        
        result.append({
            "id": event.id,
            "game_id": event.game_id,
            "game_name": game_name,
            "event_name": event.event_name,
            "event_datetime": event.event_datetime,
            "location_or_link": event.location_or_link,
            "status": event.status,
            "plan_version": event.plan_version,
            "plan_updated_at": event.plan_updated_at,
            "my_membership": my_membership,
            "is_confirmed_for_plan": is_confirmed_for_plan,
            "hosts": hosts,
            "attendees": attendees
        })
    
    return result


def update_event_plan(
    current_user_id: UUID,
    event_id: UUID,
    payload: EventPlanUpdate,
    session: Session
) -> Event:
    """Update event plan fields with atomic plan_version increment."""
    # Check event exists
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check user is HOST
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.role == MembershipRole.HOST,
            EventMembership.status == MembershipStatus.ACCEPTED
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can update event plan"
        )
    
    # Check if plan fields changed
    fields_changed = (
        (payload.event_datetime is not None and payload.event_datetime != event.event_datetime) or
        (payload.location_or_link is not None and payload.location_or_link != event.location_or_link) or
        (payload.event_name is not None and payload.event_name != event.event_name)
    )
    
    # Build update dict
    update_data = {}
    if payload.event_datetime is not None:
        update_data["event_datetime"] = payload.event_datetime
    if payload.location_or_link is not None:
        update_data["location_or_link"] = payload.location_or_link
    if payload.event_name is not None:
        update_data["event_name"] = payload.event_name
    
    if fields_changed:
        # Atomic SQL update with plan_version increment using column expression
        from sqlalchemy import update as sql_update
        values_dict = {k: v for k, v in update_data.items() if k not in ["plan_version", "plan_updated_at"]}
        # Use SQLAlchemy column expression for atomic increment
        # Event.plan_version + 1 creates a SQL expression
        stmt = (
            sql_update(Event.__table__)
            .where(Event.__table__.c.id == event_id)
            .values(
                **values_dict,
                plan_version=Event.__table__.c.plan_version + 1,
                plan_updated_at=datetime.now(timezone.utc)
            )
        )
        session.execute(stmt)
        session.commit()
    elif update_data:
        session.exec(
            update(Event)
            .where(Event.id == event_id)
            .values(**update_data)
        )
        session.commit()
    
    # Re-fetch event
    event = session.get(Event, event_id)
    return event


def set_event_status(
    current_user_id: UUID,
    event_id: UUID,
    new_status: EventStatus,
    session: Session
) -> Event:
    """Set event status (confirm/cancel) - host only."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check user is HOST
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.role == MembershipRole.HOST,
            EventMembership.status == MembershipStatus.ACCEPTED
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can change event status"
        )
    
    event.status = new_status
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def delete_event(current_user_id: UUID, event_id: UUID, session: Session) -> None:
    """Delete event - host only."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check user is HOST
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.role == MembershipRole.HOST,
            EventMembership.status == MembershipStatus.ACCEPTED
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can delete events"
        )
    
    session.delete(event)
    session.commit()


# Membership service functions

def invite_user(
    current_user_id: UUID,
    event_id: UUID,
    invitee_user_id: UUID,
    role: MembershipRole,
    session: Session
) -> EventMembership:
    """Invite a user to an event."""
    # Check event exists
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Block if event is CANCELLED
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot invite to cancelled event"
        )
    
    # Check inviter is ACCEPTED member
    inviter_membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.status == MembershipStatus.ACCEPTED
        )
    ).first()
    
    if not inviter_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ACCEPTED members may invite"
        )
    
    # Check role permissions
    if role == MembershipRole.HOST and inviter_membership.role != MembershipRole.HOST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can invite other hosts"
        )
    
    # Check existing membership
    existing = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == invitee_user_id
        )
    ).first()
    
    if existing:
        if existing.status == MembershipStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member"
            )
        elif existing.status == MembershipStatus.PENDING:
            # Idempotent - return existing
            return existing
    
    # Create new membership
    membership = EventMembership(
        event_id=event_id,
        user_id=invitee_user_id,
        role=role,
        status=MembershipStatus.PENDING
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def accept_invite(current_user_id: UUID, event_id: UUID, session: Session) -> EventMembership:
    """Accept an event invite."""
    # Check event exists
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Block if event is CANCELLED
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot accept invite to cancelled event"
        )
    
    # Require PENDING membership
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.status == MembershipStatus.PENDING
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending invite found"
        )
    
    membership.status = MembershipStatus.ACCEPTED
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def decline_invite(current_user_id: UUID, event_id: UUID, session: Session) -> None:
    """Decline an event invite by deleting the membership."""
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.status == MembershipStatus.PENDING
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending invite found"
        )
    
    session.delete(membership)
    session.commit()


def leave_event(current_user_id: UUID, event_id: UUID, session: Session) -> None:
    """Leave an event by deleting membership."""
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not a member of this event"
        )
    
    # If HOST+ACCEPTED, ensure at least one other HOST+ACCEPTED remains
    if membership.role == MembershipRole.HOST and membership.status == MembershipStatus.ACCEPTED:
        other_hosts = session.exec(
            select(EventMembership).where(
                EventMembership.event_id == event_id,
                EventMembership.role == MembershipRole.HOST,
                EventMembership.status == MembershipStatus.ACCEPTED,
                EventMembership.user_id != current_user_id
            )
        ).all()
        
        if not other_hosts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot leave: at least one ACCEPTED host must remain"
            )
    
    session.delete(membership)
    session.commit()


def confirm_current_plan(current_user_id: UUID, event_id: UUID, session: Session) -> EventMembership:
    """Confirm current plan version for user's membership."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Require ACCEPTED membership
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.status == MembershipStatus.ACCEPTED
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an ACCEPTED member to confirm plan"
        )
    
    membership.confirmed_plan_version = event.plan_version
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


# Message service functions

def list_messages(
    current_user_id: UUID,
    event_id: UUID,
    before: Optional[UUID] = None,
    limit: int = 50,
    session: Session = None
) -> List[dict]:
    """List messages for an event."""
    if session is None:
        raise ValueError("Session is required")
    
    # Require ACCEPTED membership
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.status == MembershipStatus.ACCEPTED
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an ACCEPTED member to read messages"
        )
    
    statement = select(EventMessage).where(EventMessage.event_id == event_id)
    
    if before:
        statement = statement.where(EventMessage.id < before)
    
    statement = statement.order_by(EventMessage.created_at.desc()).limit(limit)
    messages = session.exec(statement).all()
    
    # Build response with username
    result = []
    for msg in messages:
        username = None
        if msg.user_id:
            user = session.get(User, msg.user_id)
            if user:
                username = user.username
        
        result.append({
            "id": msg.id,
            "event_id": msg.event_id,
            "user_id": msg.user_id,
            "username": username,
            "content": msg.content,
            "message_type": msg.message_type,
            "created_at": msg.created_at
        })
    
    return result


def post_message(
    current_user_id: UUID,
    event_id: UUID,
    content: str,
    session: Session
) -> EventMessage:
    """Post a message to an event."""
    # Check event exists
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Block if event is CANCELLED
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot post messages to cancelled event"
        )
    
    # Require ACCEPTED membership
    membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id,
            EventMembership.status == MembershipStatus.ACCEPTED
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an ACCEPTED member to post messages"
        )
    
    message = EventMessage(
        event_id=event_id,
        user_id=current_user_id,
        content=content,
        message_type=MessageType.USER
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
