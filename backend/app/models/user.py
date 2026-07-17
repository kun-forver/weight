"""User model."""

from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text

from app.database import Base


class User(Base):
    """User account for the Fat Loss PK application."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # WeChat openid for one-click login / binding
    openid: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    nickname: Mapped[str] = mapped_column(String(50), nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[int] = mapped_column(Integer, nullable=True, comment="0=female, 1=male")
    height: Mapped[float] = mapped_column(Float, nullable=True, comment="height in cm")
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    target_weight: Mapped[float] = mapped_column(Float, nullable=True, comment="target weight in kg")
    daily_calorie_goal: Mapped[int] = mapped_column(Integer, nullable=True, comment="daily calorie goal in kcal")
    role: Mapped[str] = mapped_column(String(20), default="user", server_default=text("'user'"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    @property
    def has_password(self) -> bool:
        """Whether the user has a password set (can log in via username+password)."""
        return bool(self.password_hash)

    @property
    def wechat_bound(self) -> bool:
        """Whether the user has bound a WeChat account (openid is set)."""
        return bool(self.openid)

