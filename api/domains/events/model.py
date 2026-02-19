from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from api.domains.common.enums import EventStatus, MembershipRole, MembershipStatus, MemberSource
from api.domains.common.fields import fk_cascade


class Event(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    game_name: str = Field(nullable=False)
    event_name: str = Field(nullable=False)
    event_datetime: Optional[datetime] = None
    location_or_link: Optional[str] = None
    status: EventStatus = Field(nullable=False)
    channel_id: Optional[str] = None  # None = personal/web; set when created from integration (e.g. Discord)


class EventMembership(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("event_id", "member_id", "source", name="uq_event_member_source"),)
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(sa_column=fk_cascade("event.id", nullable=False))
    member_id: str = Field(nullable=False)
    source: MemberSource = Field(nullable=False)
    role: MembershipRole = Field(nullable=False)
    status: MembershipStatus = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
