"""Friends router: list, request, accept, search."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.friendship import Friendship
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("", response_model=list[UserResponse])
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's accepted friends."""
    friendships = (
        db.query(Friendship)
        .filter(
            Friendship.status == 1,
            (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id),
        )
        .all()
    )
    friend_ids = []
    for f in friendships:
        if f.user_id == current_user.id:
            friend_ids.append(f.friend_id)
        else:
            friend_ids.append(f.user_id)

    friends = db.query(User).filter(User.id.in_(friend_ids)).all()
    return [UserResponse.model_validate(f) for f in friends]


@router.post("/request", status_code=status.HTTP_201_CREATED)
def send_friend_request(
    friend_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a friend request to another user."""
    if friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as friend")

    friend = db.query(User).filter(User.id == friend_id).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if a friendship record already exists in either direction
    existing = (
        db.query(Friendship)
        .filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend_id))
            | ((Friendship.user_id == friend_id) & (Friendship.friend_id == current_user.id))
        )
        .first()
    )
    if existing:
        if existing.status == 1:
            raise HTTPException(status_code=400, detail="Already friends")
        if existing.status == 0:
            raise HTTPException(status_code=400, detail="Friend request already pending")

    friendship = Friendship(
        user_id=current_user.id,
        friend_id=friend_id,
        status=0,
    )
    db.add(friendship)
    db.commit()
    return {"message": "Friend request sent", "friend_id": friend_id}


@router.post("/accept")
def accept_friend_request(
    friend_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a pending friend request."""
    friendship = (
        db.query(Friendship)
        .filter(
            Friendship.user_id == friend_id,
            Friendship.friend_id == current_user.id,
            Friendship.status == 0,
        )
        .first()
    )
    if not friendship:
        raise HTTPException(status_code=404, detail="No pending friend request from this user")

    friendship.status = 1
    db.commit()
    return {"message": "Friend request accepted", "friend_id": friend_id}


@router.get("/search", response_model=list[UserResponse])
def search_friends(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search for users by username or nickname."""
    users = (
        db.query(User)
        .filter(
            User.id != current_user.id,
            (User.username.like(f"%{q}%")) | (User.nickname.like(f"%{q}%")),
        )
        .limit(20)
        .all()
    )
    return [UserResponse.model_validate(u) for u in users]
