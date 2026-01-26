from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from uuid import UUID
from typing import Optional

from api.database import SessionDep
from api.domains.auth.dependencies import current_active_user
from api.domains.users.model import User
from .schemas import GameCreate, GameRead, GameList
from . import service as game_service

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_game(
    payload: GameCreate,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Create a new game."""
    return game_service.create_game(current_user.id, payload, session)


@router.get("", response_model=GameList)
def list_games(
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """List games with optional search."""
    games = game_service.list_games(q=q, limit=limit, offset=offset, session=session)
    return GameList(games=[GameRead.model_validate(g) for g in games])


@router.get("/{game_id}", response_model=GameRead)
def get_game(
    game_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Get a game by ID."""
    return game_service.get_game(game_id, session)
