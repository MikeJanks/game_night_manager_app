from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from domains.common.enums import EventStatus, MembershipRole, MembershipStatus, MessageType


class EventCreate(BaseModel):
    """Request schema for creating an event."""
    game_id: UUID
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
    confirmed_plan_version: Optional[int] = None
    
    class Config:
        from_attributes = True


class EventCounts(BaseModel):
    """Response schema for event membership counts."""
    accepted_hosts: int
    accepted_attendees: int
    pending_invites: int


class EventMember(BaseModel):
    """Response schema for event member."""
    user_id: UUID
    username: str
    status: MembershipStatus
    
    class Config:
        from_attributes = True


class EventRead(BaseModel):
    """Response schema for event detail."""
    id: UUID
    game_id: UUID
    game_name: Optional[str] = None
    event_name: str
    event_datetime: Optional[datetime] = None
    location_or_link: Optional[str] = None
    status: EventStatus
    plan_version: int
    plan_updated_at: datetime
    my_membership: Optional[EventMembershipRead] = None
    is_confirmed_for_plan: bool
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


class MessageCreate(BaseModel):
    """Request schema for creating a message."""
    content: str


class MessageRead(BaseModel):
    """Response schema for message data."""
    id: UUID
    event_id: UUID
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    content: str
    message_type: MessageType
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageList(BaseModel):
    """Response schema for list of messages."""
    messages: list[MessageRead]
