from typing import List, Optional, Union
from dataclasses import dataclass
from sqlmodel import Session, select
from sqlalchemy import update
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone
from .model import Event, EventMembership
from .schemas import EventCreate, EventPlanUpdate, EventMembershipRead
from api.domains.users.model import User
from api.domains.common.enums import EventStatus, MembershipRole, MembershipStatus, ExternalSource


@dataclass
class ResolvedActor:
    """Actor for channel path: either app user (user_id) or external member (external_source, external_id)."""
    user_id: Optional[UUID] = None
    external_source: Optional[ExternalSource] = None
    external_id: Optional[str] = None


# --- Shared core ---

def _event_to_response_dict(
    event: Event,
    all_memberships: List[EventMembership],
    my_membership: Optional[EventMembership],
    users: dict,
) -> dict:
    """Build common event payload for both user- and channel-scoped responses."""
    my_membership_read = None
    if my_membership:
        my_membership_read = EventMembershipRead(
            role=my_membership.role,
            status=my_membership.status,
        )
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
        "my_membership": my_membership_read,
        "hosts": hosts,
        "attendees": attendees,
    }


def _find_membership_by_actor(
    session: Session,
    event_id: UUID,
    actor: ResolvedActor,
) -> Optional[EventMembership]:
    """Find membership for this event matching the actor (user_id or external)."""
    if actor.user_id is not None:
        return session.exec(
            select(EventMembership).where(
                EventMembership.event_id == event_id,
                EventMembership.user_id == actor.user_id,
            )
        ).first()
    if actor.external_source is not None and actor.external_id is not None:
        return session.exec(
            select(EventMembership).where(
                EventMembership.event_id == event_id,
                EventMembership.external_source == actor.external_source,
                EventMembership.external_id == actor.external_id,
            )
        ).first()
    return None


# --- Event service functions (legacy / used by user-scoped) ---

def create_event(current_user_id: UUID, payload: EventCreate, session: Session) -> Event:
    """Create a new event with creator as HOST."""
    event = Event(
        game_name=payload.game_name,
        event_name=payload.event_name,
        status=EventStatus.PLANNING,
        channel_id=None,
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

    all_memberships = session.exec(
        select(EventMembership).where(EventMembership.event_id == event_id)
    ).all()
    user_ids = [m.user_id for m in all_memberships if m.user_id is not None]
    users = {}
    if user_ids:
        users_list = session.exec(select(User).where(User.id.in_(user_ids))).all()
        users = {user.id: user for user in users_list}
    return _event_to_response_dict(event, all_memberships, user_membership, users)


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
        all_memberships = session.exec(
            select(EventMembership).where(EventMembership.event_id == event.id)
        ).all()
        user_ids = [m.user_id for m in all_memberships if m.user_id is not None]
        users = {}
        if user_ids:
            users_list = session.exec(select(User).where(User.id.in_(user_ids))).all()
            users = {user.id: user for user in users_list}
        result.append(_event_to_response_dict(event, all_memberships, user_membership, users))
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


# --- User-scoped (session path): same behavior as above, no channel_id ---

def list_events_for_user(
    current_user_id: UUID,
    status_filter: Optional[EventStatus] = None,
    include_cancelled: bool = False,
    limit: int = 100,
    offset: int = 0,
    session: Session = None,
) -> List[dict]:
    """List events where the user is a member. No channel_id filter."""
    return list_events_scoped(
        current_user_id,
        status_filter=status_filter,
        include_cancelled=include_cancelled,
        limit=limit,
        offset=offset,
        session=session,
    )


def get_event_for_user(current_user_id: UUID, event_id: UUID, session: Session) -> dict:
    """Get event only if user is a member. 404 otherwise."""
    return get_event_scoped(current_user_id, event_id, session)


def create_event_for_user(current_user_id: UUID, payload: EventCreate, session: Session) -> Event:
    """Create event with channel_id=None; creator as HOST."""
    return create_event(current_user_id, payload, session)


def update_event_plan_for_user(
    current_user_id: UUID,
    event_id: UUID,
    payload: EventPlanUpdate,
    session: Session,
) -> Event:
    """Update event plan - host only. User-scoped."""
    return update_event_plan(current_user_id, event_id, payload, session)


def set_event_status_for_user(
    current_user_id: UUID,
    event_id: UUID,
    new_status: EventStatus,
    session: Session,
) -> Event:
    """Set event status - host only. User-scoped."""
    return set_event_status(current_user_id, event_id, new_status, session)


def delete_event_for_user(current_user_id: UUID, event_id: UUID, session: Session) -> None:
    """Delete event - host only. User-scoped."""
    return delete_event(current_user_id, event_id, session)


def invite_user_for_user(
    current_user_id: UUID,
    event_id: UUID,
    invitee_user_id: UUID,
    role: MembershipRole,
    session: Session,
) -> EventMembership:
    """Invite a user by UUID. User-scoped."""
    return invite_user(current_user_id, event_id, invitee_user_id, role, session)


def accept_invite_for_user(current_user_id: UUID, event_id: UUID, session: Session) -> EventMembership:
    """Accept invite. User-scoped."""
    return accept_invite(current_user_id, event_id, session)


def decline_invite_for_user(current_user_id: UUID, event_id: UUID, session: Session) -> None:
    """Decline invite. User-scoped."""
    return decline_invite(current_user_id, event_id, session)


def leave_event_for_user(current_user_id: UUID, event_id: UUID, session: Session) -> None:
    """Leave event. User-scoped."""
    return leave_event(current_user_id, event_id, session)


# --- Channel-scoped (integration path): enforce event.channel_id == channel_id ---

def list_events_for_channel(
    channel_id: str,
    status_filter: Optional[EventStatus] = None,
    include_cancelled: bool = False,
    limit: int = 100,
    offset: int = 0,
    session: Session = None,
) -> List[dict]:
    """Return all events where event.channel_id == channel_id. No membership filter."""
    if session is None:
        raise ValueError("Session is required")
    statement = select(Event).where(Event.channel_id == channel_id)
    if status_filter:
        statement = statement.where(Event.status == status_filter)
    if not include_cancelled:
        statement = statement.where(Event.status != EventStatus.CANCELLED)
    statement = statement.offset(offset).limit(limit)
    events = session.exec(statement).all()
    result = []
    for event in events:
        all_memberships = session.exec(
            select(EventMembership).where(EventMembership.event_id == event.id)
        ).all()
        user_ids = [m.user_id for m in all_memberships if m.user_id is not None]
        users = {}
        if user_ids:
            users_list = session.exec(select(User).where(User.id.in_(user_ids))).all()
            users = {user.id: user for user in users_list}
        result.append(_event_to_response_dict(event, all_memberships, None, users))
    return result


def get_event_in_channel(event_id: UUID, channel_id: str, session: Session) -> dict:
    """Return event only if event.channel_id == channel_id; else 404."""
    event = session.get(Event, event_id)
    if not event or event.channel_id != channel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    all_memberships = session.exec(
        select(EventMembership).where(EventMembership.event_id == event_id)
    ).all()
    user_ids = [m.user_id for m in all_memberships if m.user_id is not None]
    users = {}
    if user_ids:
        users_list = session.exec(select(User).where(User.id.in_(user_ids))).all()
        users = {user.id: user for user in users_list}
    return _event_to_response_dict(event, all_memberships, None, users)


def create_event_in_channel(
    actor: ResolvedActor,
    payload: EventCreate,
    channel_id: str,
    session: Session,
) -> Event:
    """Create event with event.channel_id = channel_id; creator as HOST."""
    event = Event(
        game_name=payload.game_name,
        event_name=payload.event_name,
        status=EventStatus.PLANNING,
        channel_id=channel_id,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    if actor.user_id is not None:
        membership = EventMembership(
            event_id=event.id,
            user_id=actor.user_id,
            role=MembershipRole.HOST,
            status=MembershipStatus.ACCEPTED,
        )
    else:
        membership = EventMembership(
            event_id=event.id,
            user_id=None,
            external_source=actor.external_source,
            external_id=actor.external_id,
            role=MembershipRole.HOST,
            status=MembershipStatus.ACCEPTED,
        )
    session.add(membership)
    session.commit()
    return event


def _update_event_plan_by_id(event_id: UUID, payload: EventPlanUpdate, session: Session) -> Event:
    """Update event plan fields by event_id (no actor check)."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    update_data = {}
    if payload.event_datetime is not None:
        update_data["event_datetime"] = payload.event_datetime
    if payload.location_or_link is not None:
        update_data["location_or_link"] = payload.location_or_link
    if payload.event_name is not None:
        update_data["event_name"] = payload.event_name
    if update_data:
        session.exec(update(Event).where(Event.id == event_id).values(**update_data))
        session.commit()
    return session.get(Event, event_id)


def update_event_plan_in_channel(
    actor: ResolvedActor,
    event_id: UUID,
    channel_id: str,
    payload: EventPlanUpdate,
    session: Session,
) -> Event:
    """Update event plan only if event.channel_id == channel_id and actor is HOST."""
    event = session.get(Event, event_id)
    if not event or event.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    membership = _find_membership_by_actor(session, event_id, actor)
    if not membership or membership.role != MembershipRole.HOST or membership.status != MembershipStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only hosts can update event plan")
    return _update_event_plan_by_id(event_id, payload, session)


def set_event_status_in_channel(
    actor: ResolvedActor,
    event_id: UUID,
    channel_id: str,
    new_status: EventStatus,
    session: Session,
) -> Event:
    """Set event status only if event.channel_id == channel_id and actor is HOST."""
    event = session.get(Event, event_id)
    if not event or event.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    membership = _find_membership_by_actor(session, event_id, actor)
    if not membership or membership.role != MembershipRole.HOST or membership.status != MembershipStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only hosts can change event status")
    event.status = new_status
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def delete_event_in_channel(actor: ResolvedActor, event_id: UUID, channel_id: str, session: Session) -> None:
    """Delete event only if event.channel_id == channel_id and actor is HOST."""
    event = session.get(Event, event_id)
    if not event or event.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    membership = _find_membership_by_actor(session, event_id, actor)
    if not membership or membership.role != MembershipRole.HOST or membership.status != MembershipStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only hosts can delete events")
    session.delete(event)
    session.commit()


def invite_user_in_channel(
    actor: ResolvedActor,
    event_id: UUID,
    channel_id: str,
    invitee_external_id: str,
    role: MembershipRole,
    channel_member_ids: List[str],
    session: Session,
) -> EventMembership:
    """Invite by Discord id only; invitee must be in channel_member_ids."""
    if invitee_external_id not in channel_member_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invitee must be in the channel",
        )
    event = session.get(Event, event_id)
    if not event or event.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot invite to cancelled event")
    inviter_membership = _find_membership_by_actor(session, event_id, actor)
    if not inviter_membership or inviter_membership.status != MembershipStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only ACCEPTED members may invite")
    if role == MembershipRole.HOST and inviter_membership.role != MembershipRole.HOST:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only hosts can invite other hosts")
    existing = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.external_source == ExternalSource.DISCORD,
            EventMembership.external_id == invitee_external_id,
        )
    ).first()
    if existing:
        if existing.status == MembershipStatus.ACCEPTED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")
        return existing
    membership = EventMembership(
        event_id=event_id,
        user_id=None,
        external_source=ExternalSource.DISCORD,
        external_id=invitee_external_id,
        role=role,
        status=MembershipStatus.PENDING,
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def accept_invite_in_channel(actor: ResolvedActor, event_id: UUID, channel_id: str, session: Session) -> EventMembership:
    """Accept invite only if event.channel_id == channel_id."""
    event = session.get(Event, event_id)
    if not event or event.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot accept invite to cancelled event")
    membership = _find_membership_by_actor(session, event_id, actor)
    if not membership or membership.status != MembershipStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pending invite found")
    membership.status = MembershipStatus.ACCEPTED
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def decline_invite_in_channel(actor: ResolvedActor, event_id: UUID, channel_id: str, session: Session) -> None:
    """Decline invite only if event.channel_id == channel_id."""
    event = session.get(Event, event_id)
    if not event or event.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    membership = _find_membership_by_actor(session, event_id, actor)
    if not membership or membership.status != MembershipStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pending invite found")
    session.delete(membership)
    session.commit()


def leave_event_in_channel(actor: ResolvedActor, event_id: UUID, channel_id: str, session: Session) -> None:
    """Leave event only if event.channel_id == channel_id."""
    event = session.get(Event, event_id)
    if not event or event.channel_id != channel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    membership = _find_membership_by_actor(session, event_id, actor)
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a member of this event")
    if membership.role == MembershipRole.HOST and membership.status == MembershipStatus.ACCEPTED:
        other_hosts = session.exec(
            select(EventMembership).where(
                EventMembership.event_id == event_id,
                EventMembership.role == MembershipRole.HOST,
                EventMembership.status == MembershipStatus.ACCEPTED,
                EventMembership.id != membership.id,
            )
        ).all()
        if not other_hosts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot leave: at least one ACCEPTED host must remain",
            )
    session.delete(membership)
    session.commit()
