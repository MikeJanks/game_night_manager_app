from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from api.domains.common.enums import EventStatus, MembershipRole, MembershipStatus, ExternalSource
from api.domains.common.fields import fk_cascade


class Event(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    game_name: str = Field(nullable=False)
    event_name: str = Field(nullable=False)
    event_datetime: Optional[datetime] = None
    location_or_link: Optional[str] = None
    status: EventStatus = Field(nullable=False)


class EventMembership(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(sa_column=fk_cascade("event.id", nullable=False))
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    external_source: Optional[ExternalSource] = None
    external_id: Optional[str] = None
    display_name: Optional[str] = None
    role: MembershipRole = Field(nullable=False)
    status: MembershipStatus = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
