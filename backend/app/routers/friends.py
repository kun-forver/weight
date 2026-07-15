"""Friends router: list, request, accept, search."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.friendship import Friendship
from app.models.user import User
from app.schemas.user import UserResponse, FriendshipResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("", response_model=list[FriendshipResponse])
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's accepted friends and incoming pending requests."""
    friendships = (
        db.query(Friendship)
        .filter(
            Friendship.status.in_([0, 1]),
            (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id),
        )
        .all()
    )
    result = []
    for f in friendships:
        if f.status == 1:
            status_str = "accepted"
        else:
            if f.friend_id == current_user.id:
                status_str = "pending"
            else:
                status_str = "pending_outgoing"
                
        # Get friend details
        friend_id = f.friend_id if f.user_id == current_user.id else f.user_id
        friend_user = db.query(User).filter(User.id == friend_id).first()
        if not friend_user:
            continue
            
        result.append(
            FriendshipResponse(
                id=f.id,
                friend_id=friend_id,
                friend_name=friend_user.nickname or friend_user.username,
                friend_avatar=friend_user.avatar,
                status=status_str,
            )
        )
    return result


@router.post("/request", status_code=status.HTTP_201_CREATED)
def send_friend_request(
    payload: dict | None = None,
    friend_id: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a friend request to another user (supports Query param or JSON body)."""
    f_id = friend_id
    if payload:
        f_id = payload.get("friend_id") or f_id
        friend_username = payload.get("friend_username")
        if friend_username and not f_id:
            friend_user = db.query(User).filter(User.username == friend_username).first()
            if friend_user:
                f_id = friend_user.id
            else:
                raise HTTPException(status_code=404, detail="该用户不存在")
                
    if not f_id:
        raise HTTPException(status_code=400, detail="需要传入好友ID或用户名")

    if f_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能添加自己为好友")

    friend = db.query(User).filter(User.id == f_id).first()
    if not friend:
        raise HTTPException(status_code=404, detail="该用户不存在")

    # Check if a friendship record already exists in either direction
    existing = (
        db.query(Friendship)
        .filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == f_id))
            | ((Friendship.user_id == f_id) & (Friendship.friend_id == current_user.id))
        )
        .first()
    )
    if existing:
        if existing.status == 1:
            raise HTTPException(status_code=400, detail="你们已经是好友了")
        if existing.status == 0:
            raise HTTPException(status_code=400, detail="好友请求已发送，等待对方确认")

    friendship = Friendship(
        user_id=current_user.id,
        friend_id=f_id,
        status=0,
    )
    db.add(friendship)
    db.commit()
    return {"message": "Friend request sent", "friend_id": f_id}


@router.post("/accept")
def accept_friend_request(
    payload: dict | None = None,
    friend_id: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a pending friend request (supports Query param or JSON body)."""
    f_id = friend_id
    fs_id = None
    if payload:
        f_id = payload.get("friend_id") or f_id
        fs_id = payload.get("friendship_id") or payload.get("friend_id")
        
    friendship = None
    if fs_id:
        friendship = db.query(Friendship).filter(Friendship.id == fs_id).first()
    
    if not friendship and f_id:
        friendship = (
            db.query(Friendship)
            .filter(
                Friendship.user_id == f_id,
                Friendship.friend_id == current_user.id,
                Friendship.status == 0,
            )
            .first()
        )
        
    if not friendship:
        if f_id:
            friendship = db.query(Friendship).filter(Friendship.id == f_id).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="未找到待处理的好友请求")

    if friendship.friend_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能由收到请求的一方接受好友申请")

    friendship.status = 1
    db.commit()
    return {"message": "Friend request accepted", "friend_id": friendship.user_id}


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

