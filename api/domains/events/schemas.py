from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from api.domains.common.enums import EventStatus, MembershipRole, MembershipStatus


class EventCreate(BaseModel):
    """Request schema for creating an event."""
    game_name: str
    event_name: str


class EventPlanUpdate(BaseModel):
    """Request schema for updating event plan fields."""
    event_datetime: Optional[datetime] = None
    location_or_link: Optional[str] = None
    event_name: Optional[str] = None


class EventMembershipRead(BaseModel):
    """Response schema for event membership."""
    role: MembershipRole
    status: MembershipStatus

    class Config:
        from_attributes = True


class EventCounts(BaseModel):
    """Response schema for event membership counts."""
    accepted_hosts: int
    accepted_attendees: int
    pending_invites: int


class EventMember(BaseModel):
    """Response schema for event member (app user or external)."""
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    status: MembershipStatus

    class Config:
        from_attributes = True


class EventRead(BaseModel):
    """Response schema for event detail."""
    id: UUID
    game_name: str
    event_name: str
    event_datetime: Optional[datetime] = None
    location_or_link: Optional[str] = None
    status: EventStatus
    my_membership: Optional[EventMembershipRead] = None
    hosts: List[EventMember]
    attendees: List[EventMember]

    class Config:
        from_attributes = True


class EventList(BaseModel):
    """Response schema for list of events."""
    events: list[EventRead]


class InviteCreate(BaseModel):
    """Request schema for inviting a user to an event."""
    invitee_user_id: UUID
    role: MembershipRole


class InviteResponse(BaseModel):
    """Response schema for invite operations."""
    success: bool
    message: str
