from typing import List, Optional
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from uuid import UUID
from .model import Game
from .schemas import GameCreate, GameRead


def create_game(current_user_id: UUID, payload: GameCreate, session: Session) -> Game:
    """Create a new game."""
    game = Game(**payload.model_dump())
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def list_games(q: Optional[str] = None, limit: int = 100, offset: int = 0, session: Session = None) -> List[Game]:
    """List games with optional search query."""
    if session is None:
        raise ValueError("Session is required")
    
    statement = select(Game)
    
    if q:
        statement = statement.where(
            func.lower(Game.name).like(f"%{q.lower()}%")
        )
    
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


def get_game(game_id: UUID, session: Session) -> Game:
    """Get a game by ID."""
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return game
