from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy import update
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone
from .model import Event, EventMembership
from .schemas import EventCreate, EventPlanUpdate, EventMembershipRead
from api.domains.users.model import User
from api.domains.common.enums import EventStatus, MembershipRole, MembershipStatus


# Event service functions

def create_event(current_user_id: UUID, payload: EventCreate, session: Session) -> Event:
    """Create a new event with creator as HOST."""
    event = Event(
        game_name=payload.game_name,
        event_name=payload.event_name,
        status=EventStatus.PLANNING
    )
    session.add(event)
    session.commit()
    session.refresh(event)

    membership = EventMembership(
        event_id=event.id,
        user_id=current_user_id,
        role=MembershipRole.HOST,
        status=MembershipStatus.ACCEPTED
    )
    session.add(membership)
    session.commit()

    return event


def _member_display(membership: EventMembership, users: dict) -> dict:
    """Build member dict for response; handle nullable user_id (external members)."""
    if membership.user_id is not None:
        user = users.get(membership.user_id)
        username = user.username if user else None
        return {
            "user_id": membership.user_id,
            "username": username or "",
            "display_name": membership.display_name,
            "status": membership.status
        }
    return {
        "user_id": None,
        "username": None,
        "display_name": membership.display_name or "External",
        "status": membership.status
    }


def get_event_scoped(current_user_id: UUID, event_id: UUID, session: Session) -> dict:
    """Get event with scoped visibility (only if current user is a member)."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    user_membership = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user_id
        )
    ).first()

    visible = (
        user_membership is not None
        and user_membership.status in [MembershipStatus.PENDING, MembershipStatus.ACCEPTED]
    )
    if not visible:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    my_membership = None
    if user_membership:
        my_membership = EventMembershipRead(
            role=user_membership.role,
            status=user_membership.status
        )

    all_memberships = session.exec(
        select(EventMembership).where(EventMembership.event_id == event_id)
    ).all()

    user_ids = [m.user_id for m in all_memberships if m.user_id is not None]
    users = {}
    if user_ids:
        users_list = session.exec(select(User).where(User.id.in_(user_ids))).all()
        users = {user.id: user for user in users_list}

    hosts = []
    attendees = []
    for membership in all_memberships:
        member_data = _member_display(membership, users)
        if membership.role == MembershipRole.HOST:
            hosts.append(member_data)
        elif membership.role == MembershipRole.ATTENDEE:
            attendees.append(member_data)

    return {
        "id": event.id,
        "game_name": event.game_name,
        "event_name": event.event_name,
        "event_datetime": event.event_datetime,
        "location_or_link": event.location_or_link,
        "status": event.status,
        "my_membership": my_membership,
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
    """List events where the current user is a member."""
    if session is None:
        raise ValueError("Session is required")

    user_event_ids = session.exec(
        select(EventMembership.event_id).where(
            EventMembership.user_id == current_user_id,
            EventMembership.status.in_([MembershipStatus.PENDING, MembershipStatus.ACCEPTED])
        )
    ).all()

    visible_event_ids = set(user_event_ids)
    if not visible_event_ids:
        return []

    statement = select(Event).where(Event.id.in_(visible_event_ids))
    if status_filter:
        statement = statement.where(Event.status == status_filter)
    if not include_cancelled:
        statement = statement.where(Event.status != EventStatus.CANCELLED)
    statement = statement.offset(offset).limit(limit)
    events = session.exec(statement).all()

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
                status=user_membership.status
            )

        all_memberships = session.exec(
            select(EventMembership).where(EventMembership.event_id == event.id)
        ).all()
        user_ids = [m.user_id for m in all_memberships if m.user_id is not None]
        users = {}
        if user_ids:
            users_list = session.exec(select(User).where(User.id.in_(user_ids))).all()
            users = {user.id: user for user in users_list}

        hosts = []
        attendees = []
        for membership in all_memberships:
            member_data = _member_display(membership, users)
            if membership.role == MembershipRole.HOST:
                hosts.append(member_data)
            elif membership.role == MembershipRole.ATTENDEE:
                attendees.append(member_data)

        result.append({
            "id": event.id,
            "game_name": event.game_name,
            "event_name": event.event_name,
            "event_datetime": event.event_datetime,
            "location_or_link": event.location_or_link,
            "status": event.status,
            "my_membership": my_membership,
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
    """Update event plan fields (datetime, location, name)."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

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

    update_data = {}
    if payload.event_datetime is not None:
        update_data["event_datetime"] = payload.event_datetime
    if payload.location_or_link is not None:
        update_data["location_or_link"] = payload.location_or_link
    if payload.event_name is not None:
        update_data["event_name"] = payload.event_name

    if update_data:
        session.exec(
            update(Event)
            .where(Event.id == event_id)
            .values(**update_data)
        )
        session.commit()

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
    """Invite a user to an event (by user_id)."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    if event.status == EventStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot invite to cancelled event"
        )

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

    if role == MembershipRole.HOST and inviter_membership.role != MembershipRole.HOST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can invite other hosts"
        )

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
            return existing

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
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    if event.status == EventStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot accept invite to cancelled event"
        )

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

    if membership.role == MembershipRole.HOST and membership.status == MembershipStatus.ACCEPTED:
        other_hosts = session.exec(
            select(EventMembership).where(
                EventMembership.event_id == event_id,
                EventMembership.role == MembershipRole.HOST,
                EventMembership.status == MembershipStatus.ACCEPTED,
                EventMembership.id != membership.id
            )
        ).all()

        if not other_hosts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot leave: at least one ACCEPTED host must remain"
            )

    session.delete(membership)
    session.commit()
