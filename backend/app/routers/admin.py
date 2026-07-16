"""Admin router: user listing, adding users/admins, and retrieving detailed user dashboards."""

import re
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.weight_log import WeightLog
from app.schemas.user import UserResponse
from app.services.auth import get_current_user, hash_password
from app.routers.dashboard import generate_dashboard_data

router = APIRouter(prefix="/admin", tags=["admin"])


# Username validation pattern (starts with a lowercase letter, 6-8 characters, lowercase, digits, hyphens)
USERNAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]{5,7}$")

# Password validation
SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;:,.<>?/~")


def validate_password(password: str) -> str:
    """Validate password complexity: at least 8 chars, at least 2 character types."""
    if len(password) < 8:
        raise ValueError("密码至少8位")
    types = 0
    if any(c.isupper() for c in password):
        types += 1
    if any(c.islower() for c in password):
        types += 1
    if any(c.isdigit() for c in password):
        types += 1
    if any(c in SPECIAL_CHARS for c in password):
        types += 1
    if types < 2:
        raise ValueError("密码必须包含大写字母、小写字母、数字、特殊字符中的至少两种")
    return password


class AdminUserCreate(BaseModel):
    """Schema for admin to create a new user or admin."""

    username: str = Field(..., min_length=6, max_length=8)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8, max_length=128)
    nickname: str | None = None
    role: str = Field(default="user")
    gender: int | None = Field(default=None, ge=0, le=1)
    height: float | None = Field(default=None, gt=0)
    age: int | None = Field(default=None, gt=0)
    target_weight: float | None = Field(default=None, gt=0)
    daily_calorie_goal: int | None = Field(default=None, gt=0)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not USERNAME_PATTERN.match(v):
            raise ValueError("用户名6-8位，小写字母开头，只能包含小写字母、数字和连字符")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("user", "admin"):
            raise ValueError("角色必须为 'user' 或 'admin'")
        return v


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that guarantees the current user is an administrator."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有管理员权限",
        )
    return current_user


@router.get("/users", response_model=list[UserResponse])
def get_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """List all registered users in the database (admin only)."""
    users = db.query(User).order_by(User.id.desc()).all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Directly register a user or admin bypassing email verification (admin only)."""
    # Check username uniqueness
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    # Check email uniqueness
    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已注册",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname or payload.username,
        role=payload.role,
        gender=payload.gender,
        height=payload.height,
        age=payload.age,
        target_weight=payload.target_weight,
        daily_calorie_goal=payload.daily_calorie_goal or 2000,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/users/{user_id}/dashboard")
def get_user_dashboard(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Retrieve detailed dashboard and weight logs history for a specific user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该用户不存在",
        )

    # Re-use refactored dashboard generator logic
    data = generate_dashboard_data(user, db)

    # Append historical weight data for administrative oversight (last 30 logs)
    weight_logs = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user.id)
        .order_by(WeightLog.logged_at.desc())
        .limit(30)
        .all()
    )

    data["weight_history"] = [
        {
            "id": log.id,
            "weight": log.weight,
            "body_fat": log.body_fat,
            "muscle": log.muscle,
            "note": log.note,
            "logged_at": log.logged_at.isoformat() if log.logged_at else None,
        }
        for log in weight_logs
    ]

    return data
