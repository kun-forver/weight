"""PK (Fat Loss PK battle) router: active, create, accept, get, history, end."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pk_battle import PKBattle
from app.models.user import User
from app.models.weight_log import WeightLog
from app.schemas.pk import (
    PKCreate,
    PKHistoryItem,
    PKResponse,
    PKDetailsResponse,
    PKPlayerDetails,
    PKHistoryResponse,
)
from app.services.auth import get_current_user

router = APIRouter(prefix="/pk", tags=["pk"])


def _enrich_battle(battle: PKBattle, db: Session) -> PKResponse:
    """Add user nickname and avatar info to a PK battle response."""
    user_a = db.query(User).filter(User.id == battle.user_a).first()
    user_b = db.query(User).filter(User.id == battle.user_b).first()
    resp = PKResponse.model_validate(battle)
    resp.user_a_nickname = user_a.nickname if user_a else None
    resp.user_b_nickname = user_b.nickname if user_b else None
    resp.user_a_avatar = user_a.avatar if user_a else None
    resp.user_b_avatar = user_b.avatar if user_b else None
    return resp


def _get_latest_weight(user_id: int, db: Session) -> float | None:
    """Get the latest weight for a user."""
    log = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user_id)
        .order_by(WeightLog.logged_at.desc())
        .first()
    )
    return log.weight if log else None


def _get_battle_details_helper(battle: PKBattle, db: Session) -> PKDetailsResponse:
    """Build the nested PK details structure expected by the frontend."""
    user_a = db.query(User).filter(User.id == battle.user_a).first()
    user_b = db.query(User).filter(User.id == battle.user_b).first()
    
    current_a = _get_latest_weight(battle.user_a, db) or battle.start_weight_a or 0.0
    current_b = _get_latest_weight(battle.user_b, db) or battle.start_weight_b or 0.0
    
    score_a = round(battle.start_weight_a - current_a, 2) if battle.start_weight_a else 0.0
    score_b = round(battle.start_weight_b - current_b, 2) if battle.start_weight_b else 0.0
    
    # Correct formula: weight lost / target loss * 100
    pct_a = round((score_a / battle.target_a) * 100, 1) if (battle.target_a and battle.target_a > 0) else 0.0
    pct_b = round((score_b / battle.target_b) * 100, 1) if (battle.target_b and battle.target_b > 0) else 0.0
    
    pct_a = max(0.0, pct_a)
    pct_b = max(0.0, pct_b)
    
    leader = None
    if pct_a > pct_b:
        leader = battle.user_a
    elif pct_b > pct_a:
        leader = battle.user_b
        
    days_total = (battle.end_date - battle.start_date).days if (battle.end_date and battle.start_date) else 30
    days_elapsed = (date.today() - battle.start_date).days if battle.start_date else 0
    days_elapsed = max(0, days_elapsed)
    
    status_map = {0: "pending", 1: "active", 2: "completed", 3: "cancelled"}
    status_str = status_map.get(battle.status, "active")
    
    return PKDetailsResponse(
        id=battle.id,
        name=battle.name,
        status=status_str,
        reward=battle.reward,
        days_total=days_total,
        days_elapsed=days_elapsed,
        leader=leader,
        user_a=PKPlayerDetails(
            id=battle.user_a,
            name=user_a.nickname or user_a.username if user_a else "我",
            avatar=user_a.avatar,
            score=score_a,
            pct=pct_a,
        ),
        user_b=PKPlayerDetails(
            id=battle.user_b,
            name=user_b.nickname or user_b.username if user_b else "对手",
            avatar=user_b.avatar,
            score=score_b,
            pct=pct_b,
        )
    )


@router.get("/active", response_model=list[PKDetailsResponse])
def get_active_battles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all active (pending and ongoing) PK battles involving the current user."""
    battles = (
        db.query(PKBattle)
        .filter(
            PKBattle.status.in_([0, 1]),
            (PKBattle.user_a == current_user.id) | (PKBattle.user_b == current_user.id),
        )
        .order_by(PKBattle.created_at.desc())
        .all()
    )
    return [_get_battle_details_helper(b, db) for b in battles]


@router.post("", response_model=PKResponse, status_code=status.HTTP_201_CREATED)
def create_pk(
    payload: PKCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new PK battle (status=pending, waits for opponent to accept)."""
    opponent = db.query(User).filter(User.id == payload.user_b).first()
    if not opponent:
        raise HTTPException(status_code=404, detail="Opponent user not found")
    if payload.user_b == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot PK with yourself")
    if opponent.role == "admin":
        raise HTTPException(status_code=400, detail="不能向管理员账号发起对战")

    if payload.end_date <= date.today():
        raise HTTPException(status_code=400, detail="End date must be in the future")

    start_weight_a = _get_latest_weight(current_user.id, db)
    start_weight_b = _get_latest_weight(payload.user_b, db)

    battle = PKBattle(
        name=payload.name,
        user_a=current_user.id,
        user_b=payload.user_b,
        start_date=date.today(),
        end_date=payload.end_date,
        target_a=payload.target_a,
        target_b=payload.target_b,
        start_weight_a=start_weight_a or 0,
        start_weight_b=start_weight_b or 0,
        reward=payload.reward,
        status=0,  # pending
    )
    db.add(battle)
    db.commit()
    db.refresh(battle)
    return _enrich_battle(battle, db)


@router.post("/{battle_id}/accept", response_model=PKResponse)
def accept_pk(
    battle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a pending PK battle (only the invited opponent can accept)."""
    battle = db.query(PKBattle).filter(PKBattle.id == battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="PK battle not found")
    if battle.status != 0:
        raise HTTPException(status_code=400, detail="PK battle is not pending")
    if battle.user_b != current_user.id:
        raise HTTPException(status_code=403, detail="Only the invited opponent can accept")

    # Record starting weights at acceptance time if not already set
    if not battle.start_weight_a:
        battle.start_weight_a = _get_latest_weight(battle.user_a, db) or 0
    if not battle.start_weight_b:
        battle.start_weight_b = _get_latest_weight(battle.user_b, db) or 0

    battle.status = 1  # active
    db.commit()
    db.refresh(battle)
    return _enrich_battle(battle, db)


@router.get("/history", response_model=list[PKHistoryResponse])
def get_pk_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get PK battle history for the current user (completed and cancelled)."""
    battles = (
        db.query(PKBattle)
        .filter(
            (PKBattle.user_a == current_user.id) | (PKBattle.user_b == current_user.id),
            PKBattle.status.in_([2, 3]),  # completed or cancelled
        )
        .order_by(PKBattle.created_at.desc())
        .all()
    )
    result = []
    for b in battles:
        # Determine opponent
        opp_id = b.user_b if b.user_a == current_user.id else b.user_a
        opp = db.query(User).filter(User.id == opp_id).first()
        opp_name = opp.nickname or opp.username if opp else "对手"
        
        # Get weight lost (score)
        current_a = _get_latest_weight(b.user_a, db) or b.start_weight_a or 0.0
        current_b = _get_latest_weight(b.user_b, db) or b.start_weight_b or 0.0
        
        score_a = round(b.start_weight_a - current_a, 2) if b.start_weight_a else 0.0
        score_b = round(b.start_weight_b - current_b, 2) if b.start_weight_b else 0.0
        
        my_score = score_a if b.user_a == current_user.id else score_b
        rival_score = score_b if b.user_a == current_user.id else score_a
        
        # Determine result
        if b.status == 3:  # cancelled
            res = "draw"
        elif b.winner == current_user.id:
            res = "win"
        elif b.winner is not None:
            res = "lose"
        else:
            res = "draw"
            
        result.append(
            PKHistoryResponse(
                id=b.id,
                name=b.name,
                start_date=b.start_date,
                end_date=b.end_date,
                result=res,
                rival_name=opp_name,
                my_score=my_score,
                rival_score=rival_score,
            )
        )
    return result


@router.get("/{battle_id}", response_model=PKResponse)
def get_pk(
    battle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific PK battle."""
    battle = db.query(PKBattle).filter(PKBattle.id == battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="PK battle not found")
    if battle.user_a != current_user.id and battle.user_b != current_user.id:
        raise HTTPException(status_code=403, detail="You are not part of this PK battle")
    return _enrich_battle(battle, db)


@router.post("/{battle_id}/end", response_model=PKResponse)
def end_pk(
    battle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """End a PK battle and determine the winner."""
    battle = db.query(PKBattle).filter(PKBattle.id == battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="PK battle not found")
    if battle.user_a != current_user.id and battle.user_b != current_user.id:
        raise HTTPException(status_code=403, detail="You are not part of this PK battle")
    if battle.status != 1:
        raise HTTPException(status_code=400, detail="PK battle is not active")

    current_a = _get_latest_weight(battle.user_a, db) or battle.start_weight_a or 0.0
    current_b = _get_latest_weight(battle.user_b, db) or battle.start_weight_b or 0.0

    winner_id = None
    # Calculate progress = weight lost / target loss
    progress_a = (battle.start_weight_a - current_a) / battle.target_a if battle.target_a > 0 else 0
    progress_b = (battle.start_weight_b - current_b) / battle.target_b if battle.target_b > 0 else 0
    winner_id = battle.user_a if progress_a >= progress_b else battle.user_b

    battle.status = 2  # completed
    battle.winner = winner_id
    db.commit()
    db.refresh(battle)
    return _enrich_battle(battle, db)

