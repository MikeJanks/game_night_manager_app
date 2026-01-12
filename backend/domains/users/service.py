from typing import List, Optional
from sqlmodel import Session, select, func, or_
from fastapi import HTTPException, status
from uuid import UUID
from .model import User, Friendship
from .schemas import UserCreate, UserUpdate
from backend.domains.common.enums import FriendshipStatus


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


# Friend service functions

def send_friend_request(current_user_id: UUID, target_user_id: UUID, session: Session) -> Friendship:
    """Send a friend request from current_user to target_user."""
    # Prevent self-friending
    if current_user_id == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send friend request to yourself"
        )
    
    # Check if an accepted friendship already exists (either direction)
    accepted_friendship = session.exec(
        select(Friendship).where(
            or_(
                (Friendship.user_id == current_user_id) & (Friendship.friend_user_id == target_user_id),
                (Friendship.user_id == target_user_id) & (Friendship.friend_user_id == current_user_id)
            ),
            Friendship.status == FriendshipStatus.ACCEPTED
        )
    ).first()
    
    if accepted_friendship:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Friendship already exists"
        )
    
    # Check if a pending request already exists in either direction
    pending_friendship = session.exec(
        select(Friendship).where(
            or_(
                (Friendship.user_id == current_user_id) & (Friendship.friend_user_id == target_user_id),
                (Friendship.user_id == target_user_id) & (Friendship.friend_user_id == current_user_id)
            ),
            Friendship.status == FriendshipStatus.PENDING
        )
    ).first()
    
    if pending_friendship:
        # If same direction, return existing (idempotent)
        if pending_friendship.user_id == current_user_id and pending_friendship.friend_user_id == target_user_id:
            return pending_friendship
        # If opposite direction, return 409
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Friend request already exists"
        )
    
    # Create new friend request
    friendship = Friendship(
        user_id=current_user_id,
        friend_user_id=target_user_id,
        status=FriendshipStatus.PENDING
    )
    session.add(friendship)
    session.commit()
    session.refresh(friendship)
    return friendship


def accept_friend_request(current_user_id: UUID, from_user_id: UUID, session: Session) -> tuple[Friendship, Friendship]:
    """Accept a friend request from from_user_id to current_user_id."""
    # Find incoming pending row
    incoming = session.exec(
        select(Friendship).where(
            Friendship.user_id == from_user_id,
            Friendship.friend_user_id == current_user_id,
            Friendship.status == FriendshipStatus.PENDING
        )
    ).first()
    
    if not incoming:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )
    
    # Set incoming to ACCEPTED
    incoming.status = FriendshipStatus.ACCEPTED
    session.add(incoming)
    
    # Ensure reciprocal row exists
    reciprocal = session.exec(
        select(Friendship).where(
            Friendship.user_id == current_user_id,
            Friendship.friend_user_id == from_user_id
        )
    ).first()
    
    if not reciprocal:
        reciprocal = Friendship(
            user_id=current_user_id,
            friend_user_id=from_user_id,
            status=FriendshipStatus.ACCEPTED
        )
        session.add(reciprocal)
    else:
        reciprocal.status = FriendshipStatus.ACCEPTED
        session.add(reciprocal)
    
    session.commit()
    session.refresh(incoming)
    session.refresh(reciprocal)
    return incoming, reciprocal


def decline_friend_request(current_user_id: UUID, from_user_id: UUID, session: Session) -> None:
    """Decline a friend request by deleting the incoming pending row."""
    incoming = session.exec(
        select(Friendship).where(
            Friendship.user_id == from_user_id,
            Friendship.friend_user_id == current_user_id,
            Friendship.status == FriendshipStatus.PENDING
        )
    ).first()
    
    if not incoming:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )
    
    session.delete(incoming)
    session.commit()


def list_friends(current_user_id: UUID, session: Session) -> List[dict]:
    """List all accepted friends of current_user."""
    # Get friendships where current_user is involved and status is ACCEPTED
    friendships = session.exec(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.ACCEPTED,
            or_(
                Friendship.user_id == current_user_id,
                Friendship.friend_user_id == current_user_id
            )
        )
    ).all()
    
    friends = []
    friend_ids = set()
    for friendship in friendships:
        # Determine which user is the friend (not current_user)
        friend_id = friendship.friend_user_id if friendship.user_id == current_user_id else friendship.user_id
        if friend_id not in friend_ids:
            friend_ids.add(friend_id)
            user = session.get(User, friend_id)
            if user:
                friends.append({
                    "user_id": user.id,
                    "username": user.username,
                    "status": friendship.status,
                    "created_at": friendship.created_at
                })
    
    return friends


def list_friend_requests(current_user_id: UUID, session: Session) -> dict:
    """List incoming and outgoing pending friend requests."""
    # Incoming requests (others requesting current_user)
    incoming_friendships = session.exec(
        select(Friendship).where(
            Friendship.friend_user_id == current_user_id,
            Friendship.status == FriendshipStatus.PENDING
        )
    ).all()
    
    incoming_list = []
    for friendship in incoming_friendships:
        user = session.get(User, friendship.user_id)
        if user:
            incoming_list.append({
                "user_id": user.id,
                "username": user.username,
                "direction": "incoming",
                "created_at": friendship.created_at
            })
    
    # Outgoing requests (current_user requesting others)
    outgoing_friendships = session.exec(
        select(Friendship).where(
            Friendship.user_id == current_user_id,
            Friendship.status == FriendshipStatus.PENDING
        )
    ).all()
    
    outgoing_list = []
    for friendship in outgoing_friendships:
        user = session.get(User, friendship.friend_user_id)
        if user:
            outgoing_list.append({
                "user_id": user.id,
                "username": user.username,
                "direction": "outgoing",
                "created_at": friendship.created_at
            })
    
    return {
        "incoming": incoming_list,
        "outgoing": outgoing_list
    }

