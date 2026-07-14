"""Weight router: list, create, today, latest."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.weight_log import WeightLog
from app.schemas.weight import WeightCreate, WeightResponse, WeightSummary
from app.services.auth import get_current_user

router = APIRouter(prefix="/weights", tags=["weight"])


@router.get("", response_model=list[WeightResponse])
def get_weights(
    range_param: str = Query("7d", alias="range"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get weight logs for a given range: 7d, 30d, or all."""
    query = db.query(WeightLog).filter(WeightLog.user_id == current_user.id)

    if range_param == "7d":
        start = datetime.utcnow() - timedelta(days=7)
        query = query.filter(WeightLog.logged_at >= start)
    elif range_param == "30d":
        start = datetime.utcnow() - timedelta(days=30)
        query = query.filter(WeightLog.logged_at >= start)
    elif range_param == "all":
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid range, use 7d, 30d, or all")

    logs = query.order_by(WeightLog.logged_at.desc()).all()
    return [WeightResponse.model_validate(log) for log in logs]


@router.post("", response_model=WeightResponse, status_code=status.HTTP_201_CREATED)
def create_weight(
    payload: WeightCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new weight log entry. If a log already exists today, update it."""
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)

    # Check if there is already a log today
    existing = (
        db.query(WeightLog)
        .filter(
            WeightLog.user_id == current_user.id,
            WeightLog.logged_at >= today_start,
            WeightLog.logged_at < today_end,
        )
        .first()
    )

    if existing:
        # Update existing
        existing.weight = payload.weight
        if payload.body_fat is not None:
            existing.body_fat = payload.body_fat
        if payload.muscle is not None:
            existing.muscle = payload.muscle
        if payload.note is not None:
            existing.note = payload.note
        db.commit()
        db.refresh(existing)
        return WeightResponse.model_validate(existing)

    log = WeightLog(
        user_id=current_user.id,
        weight=payload.weight,
        body_fat=payload.body_fat,
        muscle=payload.muscle,
        note=payload.note,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return WeightResponse.model_validate(log)


@router.get("/today", response_model=WeightResponse | None)
def get_weight_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get today's weight log entry, if any."""
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)

    log = (
        db.query(WeightLog)
        .filter(
            WeightLog.user_id == current_user.id,
            WeightLog.logged_at >= today_start,
            WeightLog.logged_at < today_end,
        )
        .first()
    )
    if not log:
        return None
    return WeightResponse.model_validate(log)


@router.get("/latest", response_model=WeightResponse | None)
def get_latest_weight(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the most recent weight log entry."""
    log = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == current_user.id)
        .order_by(WeightLog.logged_at.desc())
        .first()
    )
    if not log:
        return None
    return WeightResponse.model_validate(log)
