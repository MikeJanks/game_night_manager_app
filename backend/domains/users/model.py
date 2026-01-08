from fastapi_users_db_sqlmodel import SQLModelBaseUserDB
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from domains.common.enums import FriendshipStatus
from domains.common.fields import fk_cascade


class User(SQLModelBaseUserDB, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, nullable=False)


class Friendship(SQLModel, table=True):
    user_id: UUID = Field(sa_column=fk_cascade("user.id", primary_key=True))
    friend_user_id: UUID = Field(sa_column=fk_cascade("user.id", primary_key=True))
    status: FriendshipStatus = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    responded_at: Optional[datetime] = None
