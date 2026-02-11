import os
from typing import Annotated, Optional
from uuid import UUID
from fastapi import Depends, Request
from fastapi_users import BaseUserManager
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from sqlmodel import Session, select

from api.domains.users.model import User
from api.database import get_session


class CustomUserDatabase(SQLModelUserDatabase[User, UUID]):
    """Custom user database that supports login with both email and username."""
    
    async def get_by_email(self, email_or_username: str) -> Optional[User]:
        """Override to support both email and username lookup."""
        # First try email (default behavior)
        try:
            user = await super().get_by_email(email_or_username)
            if user:
                return user
        except Exception:
            # If email lookup fails, try username
            pass
        
        # If not found by email, try username
        statement = select(User).where(User.username == email_or_username)
        result = self.session.exec(statement)
        return result.first()


def get_user_db(session: Session = Depends(get_session)):
    """Get user database adapter for fastapi-users."""
    yield CustomUserDatabase(session, User)


# Get secret key from environment variable
# Fallback to a default for development (NOT for production)
SECRET = os.getenv("SECRET_KEY")


class UserManager(BaseUserManager[User, UUID]):
    """User manager for fastapi-users with JWT authentication."""
    
    def __init__(self, user_db: CustomUserDatabase, secret: str):
        super().__init__(user_db)
        self.secret = secret
    
    def parse_id(self, value: str) -> UUID:
        """Parse string ID from JWT token to UUID."""
        return UUID(value)
    
    async def validate_password(self, password: str, user: User) -> None:
        """Validate password - fastapi-users handles hashing automatically."""
        # Password validation is handled by fastapi-users
        # This method can be used for additional validation rules if needed
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
    
    async def on_after_register(self, user: User, request: Optional[Request] = None) -> None:
        """Called after user registration."""
        pass


async def get_user_manager(user_db=Depends(get_user_db)):
    """Get user manager instance."""
    yield UserManager(user_db, SECRET)


# JWT Authentication Backend
bearer_transport = BearerTransport(tokenUrl="api/auth/login")

def get_jwt_strategy() -> JWTStrategy[User, UUID]:
    """Get JWT strategy for authentication."""
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

jwt_authentication = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Create FastAPIUsers instance with JWT backend
fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [jwt_authentication]
)


# Export current_active_user dependency
current_active_user = fastapi_users.current_user(active=True)
