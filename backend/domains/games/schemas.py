from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class GameCreate(BaseModel):
    """Request schema for creating a game."""
    name: str
    description: Optional[str] = None
    player_count: Optional[int] = None


class GameRead(BaseModel):
    """Response schema for game data."""
    id: UUID
    name: str
    description: Optional[str] = None
    player_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class GameList(BaseModel):
    """Response schema for list of games."""
    games: list[GameRead]
