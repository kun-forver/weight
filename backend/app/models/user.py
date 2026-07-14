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
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[int] = mapped_column(Integer, nullable=True, comment="0=female, 1=male")
    height: Mapped[float] = mapped_column(Float, nullable=True, comment="height in cm")
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    target_weight: Mapped[float] = mapped_column(Float, nullable=True, comment="target weight in kg")
    daily_calorie_goal: Mapped[int] = mapped_column(Integer, nullable=True, comment="daily calorie goal in kcal")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
