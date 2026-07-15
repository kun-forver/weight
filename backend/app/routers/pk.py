"""PK (Fat Loss PK battle) router: active, create, accept, get, history, end."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pk_battle import PKBattle
from app.models.user import User
from app.models.weight_log import WeightLog
from app.schemas.pk import PKCreate, PKHistoryItem, PKResponse
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


@router.get("/active", response_model=list[PKResponse])
def get_active_battles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all active PK battles involving the current user."""
    battles = (
        db.query(PKBattle)
        .filter(
            PKBattle.status == 1,
            (PKBattle.user_a == current_user.id) | (PKBattle.user_b == current_user.id),
        )
        .order_by(PKBattle.created_at.desc())
        .all()
    )
    return [_enrich_battle(b, db) for b in battles]


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


@router.get("/history", response_model=list[PKHistoryItem])
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
        user_a = db.query(User).filter(User.id == b.user_a).first()
        user_b = db.query(User).filter(User.id == b.user_b).first()
        item = PKHistoryItem.model_validate(b)
        item.user_a_nickname = user_a.nickname if user_a else None
        item.user_b_nickname = user_b.nickname if user_b else None
        result.append(item)
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

    # Determine winner based on who reached closer to their target
    current_a = _get_latest_weight(battle.user_a, db)
    current_b = _get_latest_weight(battle.user_b, db)

    winner_id = None
    if current_a is not None and current_b is not None:
        progress_a = (battle.start_weight_a - current_a) / (battle.start_weight_a - battle.target_a) if battle.start_weight_a != battle.target_a else 0
        progress_b = (battle.start_weight_b - current_b) / (battle.start_weight_b - battle.target_b) if battle.start_weight_b != battle.target_b else 0
        winner_id = battle.user_a if progress_a >= progress_b else battle.user_b

    battle.status = 2  # completed
    battle.winner = winner_id
    db.commit()
    db.refresh(battle)
    return _enrich_battle(battle, db)
