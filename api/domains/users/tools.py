from typing import Optional, Dict, Any
from langchain_core.tools import tool
from sqlmodel import Session
from uuid import UUID
from . import service as user_service
from .schemas import UserCreate, UserUpdate


def create_user_tools(session: Session):
    """Create user-related tools bound to a database session."""
    
    @tool
    def get_all_users() -> Dict[str, Any]:
        """Retrieve all users from the database.
        
        Returns a dict with a 'users' key containing a list of all users 
        with their id, username, email, and created_at timestamp.
        Use this when you need to see all users or find a user by browsing the list.
        """
        users = user_service.get_all_users(session)
        return {"users": [user.model_dump() for user in users]}
    
    @tool
    def get_user_by_id(user_id: str) -> Dict[str, Any]:
        """Retrieve a specific user by their unique ID.
        
        Args:
            user_id: The UUID of the user (string)
        
        Returns a dict with a 'user' key containing the user's information 
        including id, username, email, and created_at.
        Returns {"user": None} if the user doesn't exist.
        Use this when you know the user's ID and need their details.
        """
        user = user_service.get_user_by_id(UUID(user_id), session)
        return {"user": user.model_dump() if user else None}
    
    @tool
    def create_user(username: str, email: str) -> Dict[str, Any]:
        """Create a new user account.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        IMPORTANT: This tool REQUIRES both username and email to be provided. 
        If the user hasn't provided these values, you MUST ask them for this information 
        before calling this tool. Do NOT call this tool with empty strings or placeholder values.
        
        Args:
            username: A unique username for the new user (must not already exist) - REQUIRED
            email: A unique email address for the new user (must not already exist) - REQUIRED
        
        Returns a dict with a 'user' key containing the newly created user 
        with their assigned ID and created_at timestamp.
        Raises an error if username or email already exists.
        Use this to register a new user in the system.
        """
        user_data = UserCreate(username=username, email=email)
        user = user_service.create_user(user_data, session)
        return {"user": user.model_dump()}
    
    @tool
    def update_user(user_id: str, username: Optional[str] = None,
                   email: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing user's information.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user to update (string)
            username: Optional new username (must be unique if provided)
            email: Optional new email address (must be unique if provided)
        
        Returns a dict with a 'user' key containing the updated user information.
        Only provide the fields you want to change - other fields remain unchanged.
        Raises an error if the user doesn't exist or if the new username/email already exists.
        """
        user_update = UserUpdate(username=username, email=email)
        user = user_service.update_user(UUID(user_id), user_update, session)
        return {"user": user.model_dump()}
    
    @tool
    def delete_user(user_id: str) -> Dict[str, Any]:
        """Permanently delete a user from the database.
        
        ⚠️ WRITE OPERATION: This modifies the database. Present information and request confirmation before calling.
        
        Args:
            user_id: The UUID of the user to delete (string)
        
        Returns a dict with a 'success' key set to True if the user was successfully deleted.
        Raises an error if the user doesn't exist.
        Warning: This action cannot be undone.
        """
        result = user_service.delete_user(UUID(user_id), session)
        return {"success": result}
    
    @tool
    def filter_users(username: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
        """Filter users by partial matches on username or email.
        
        Args:
            username: Optional partial match for username (case-insensitive)
            email: Optional partial match for email address (case-insensitive)
        
        Returns a dict with a 'users' key containing a list of users that match 
        any of the provided search criteria.
        All provided filters are combined with AND logic (all must match).
        Use this to search for users when you know part of the username or email.
        """
        users = user_service.filter_users(session, username=username, email=email)
        return {"users": [user.model_dump() for user in users]}
    
    return [
        get_all_users,
        get_user_by_id,
        update_user,
        filter_users,
    ]
