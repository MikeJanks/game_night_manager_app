from typing import Dict, Any, Optional
from langchain_core.tools import tool
from sqlmodel import Session
from uuid import UUID

from . import service as game_service
from .schemas import GameCreate


def create_game_tools(session: Session, current_user_id: UUID):
    """Create game-related tools bound to a database session and user."""
    
    @tool
    def create_game(name: str, description: Optional[str] = None, player_count: Optional[int] = None) -> Dict[str, Any]:
        """Create a new game.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            name: The name of the game (required)
            description: Optional description of the game
            player_count: Optional number of players
        
        Returns a dict with a 'game' key containing the created game.
        """
        payload = GameCreate(name=name, description=description, player_count=player_count)
        game = game_service.create_game(current_user_id, payload, session)
        return {"game": game.model_dump()}
    
    @tool
    def list_games(q: Optional[str] = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List games with optional search query.
        
        Args:
            q: Optional search query to filter games by name
            limit: Maximum number of games to return (default: 100)
            offset: Number of games to skip (default: 0)
        
        Returns a dict with a 'games' key containing a list of games.
        """
        games = game_service.list_games(q=q, limit=limit, offset=offset, session=session)
        return {"games": [game.model_dump() for game in games]}
    
    @tool
    def get_game(game_id: str) -> Dict[str, Any]:
        """Get a game by ID.
        
        Args:
            game_id: The UUID of the game
        
        Returns a dict with a 'game' key containing the game, or None if not found.
        """
        try:
            game = game_service.get_game(UUID(game_id), session)
            return {"game": game.model_dump()}
        except Exception as e:
            return {"game": None, "error": str(e)}
    
    return [
        create_game,
        list_games,
        get_game,
    ]
