from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from backend.domains.common.enums import EventStatus, MembershipRole, MembershipStatus, MessageType
from backend.domains.common.fields import fk_cascade


class Event(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    game_id: UUID = Field(foreign_key="game.id", nullable=False)
    event_name: str = Field(nullable=False)
    event_datetime: Optional[datetime] = None
    location_or_link: Optional[str] = None
    status: EventStatus = Field(nullable=False)
    plan_version: int = Field(default=1, nullable=False)
    plan_updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class EventMembership(SQLModel, table=True):
    event_id: UUID = Field(sa_column=fk_cascade("event.id", primary_key=True))
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role: MembershipRole = Field(nullable=False)
    status: MembershipStatus = Field(nullable=False)
    confirmed_plan_version: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class EventMessage(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(sa_column=fk_cascade("event.id", nullable=False))
    user_id: Optional[UUID] = Field(foreign_key="user.id", nullable=True)
    content: str = Field(nullable=False)
    message_type: MessageType = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
