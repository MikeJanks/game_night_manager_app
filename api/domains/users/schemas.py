from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from fastapi_users.schemas import BaseUserCreate, BaseUserUpdate, BaseUser


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
