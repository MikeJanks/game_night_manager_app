from sqlmodel import Field, SQLModel
from typing import Optional
from uuid import UUID, uuid4


class Game(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = None
    player_count: Optional[int] = None
