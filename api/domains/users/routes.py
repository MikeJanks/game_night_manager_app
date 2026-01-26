from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID

from api.database import SessionDep
from api.domains.auth.dependencies import current_active_user
from api.domains.users.model import User
from .schemas import (
    FriendRequestCreate, FriendList, FriendRequestList, FriendRead, FriendRequestRead
)
from . import service as user_service

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("/request", status_code=status.HTTP_201_CREATED)
def send_friend_request(
    payload: FriendRequestCreate,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Send a friend request."""
    try:
        friendship = user_service.send_friend_request(
            current_user.id, payload.target_user_id, session
        )
        return {"success": True, "message": "Friend request sent"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/accept", status_code=status.HTTP_200_OK)
def accept_friend_request(
    user_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Accept a friend request."""
    try:
        user_service.accept_friend_request(current_user.id, user_id, session)
        return {"success": True, "message": "Friend request accepted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/decline", status_code=status.HTTP_200_OK)
def decline_friend_request(
    user_id: UUID,
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """Decline a friend request."""
    try:
        user_service.decline_friend_request(current_user.id, user_id, session)
        return {"success": True, "message": "Friend request declined"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=FriendList)
def list_friends(
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """List all accepted friends."""
    friends_data = user_service.list_friends(current_user.id, session)
    friends = [FriendRead(**f) for f in friends_data]
    return FriendList(friends=friends)


@router.get("/requests", response_model=FriendRequestList)
def list_friend_requests(
    current_user: User = Depends(current_active_user),
    session: SessionDep = None
):
    """List incoming and outgoing pending friend requests."""
    requests_data = user_service.list_friend_requests(current_user.id, session)
    all_requests = requests_data["incoming"] + requests_data["outgoing"]
    requests = [FriendRequestRead(**r) for r in all_requests]
    return FriendRequestList(requests=requests)
