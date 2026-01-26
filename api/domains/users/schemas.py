from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi_users.schemas import BaseUserCreate, BaseUserUpdate, BaseUser
from api.domains.common.enums import FriendshipStatus


class UserPublic(BaseUser):
    """Response schema for user data."""
    username: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserCreate(BaseUserCreate):
    """Request schema for creating a user."""
    username: str


class UserUpdate(BaseUserUpdate):
    """Request schema for updating a user."""
    username: Optional[str] = None


class FriendRequestCreate(BaseModel):
    """Request schema for creating a friend request."""
    target_user_id: UUID


class FriendRead(BaseModel):
    """Response schema for friend data."""
    user_id: UUID
    username: str
    status: FriendshipStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class FriendRequestRead(BaseModel):
    """Response schema for friend request data."""
    user_id: UUID
    username: str
    direction: str  # "incoming" or "outgoing"
    created_at: datetime
    
    class Config:
        from_attributes = True


class FriendList(BaseModel):
    """Response schema for list of friends."""
    friends: list[FriendRead]


class FriendRequestList(BaseModel):
    """Response schema for list of friend requests."""
    requests: list[FriendRequestRead]
