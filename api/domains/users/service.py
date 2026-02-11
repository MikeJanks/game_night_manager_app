from typing import List, Optional
from sqlmodel import Session, select, func
from uuid import UUID
from .model import User
from .schemas import UserCreate, UserUpdate


def get_all_users(session: Session) -> List[User]:
    """Get all users from the database."""
    statement = select(User)
    return session.exec(statement).all()


def filter_users(
    session: Session,
    username: Optional[str] = None,
    email: Optional[str] = None
) -> List[User]:
    """Filter users by partial matches on username or email."""
    statement = select(User)
    if username:
        statement = statement.where(func.lower(User.username).like(f"%{username.lower()}%"))
    if email:
        statement = statement.where(func.lower(User.email).like(f"%{email.lower()}%"))
    return session.exec(statement).all()


def get_user_by_id(user_id: UUID, session: Session) -> Optional[User]:
    """Get a user by ID. Returns None if not found."""
    return session.get(User, user_id)


def get_user_by_username(username: str, session: Session) -> Optional[User]:
    """Get a user by exact username match. Returns None if not found."""
    return session.exec(select(User).where(User.username == username)).first()


def create_user(user_data: UserCreate, session: Session) -> User:
    """Create a new user with validation for username and email uniqueness."""
    # Check if username already exists
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise ValueError("Username already exists")
    
    # Check if email already exists
    existing_email = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_email:
        raise ValueError("Email already exists")
    
    db_user = User(**user_data.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(user_id: UUID, user_update: UserUpdate, session: Session) -> User:
    """Update a user with validation for username and email uniqueness."""
    user = session.get(User, user_id)
    if not user:
        raise ValueError("User not found")
    
    # Check if username is being updated and already exists
    if user_update.username is not None and user_update.username != user.username:
        existing_user = session.exec(select(User).where(User.username == user_update.username)).first()
        if existing_user:
            raise ValueError("Username already exists")
    
    # Check if email is being updated and already exists
    if user_update.email is not None and user_update.email != user.email:
        existing_email = session.exec(select(User).where(User.email == user_update.email)).first()
        if existing_email:
            raise ValueError("Email already exists")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(user_id: UUID, session: Session) -> bool:
    """Delete a user by ID. Returns True if deleted, False if not found."""
    user = session.get(User, user_id)
    if not user:
        raise ValueError("User not found")
    
    session.delete(user)
    session.commit()
    return True
