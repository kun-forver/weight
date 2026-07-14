"""PKBattle model."""

from datetime import date, datetime

from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PKBattle(Base):
    """A weight-loss PK (competition) battle between two users."""

    __tablename__ = "pk_battles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_a: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_b: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_a: Mapped[float] = mapped_column(Float, nullable=False, comment="target weight for user A in kg")
    target_b: Mapped[float] = mapped_column(Float, nullable=False, comment="target weight for user B in kg")
    start_weight_a: Mapped[float] = mapped_column(Float, nullable=False, comment="starting weight of user A in kg")
    start_weight_b: Mapped[float] = mapped_column(Float, nullable=False, comment="starting weight of user B in kg")
    reward: Mapped[str] = mapped_column(String(255), nullable=True, comment="reward for the winner")
    status: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="0=pending, 1=active, 2=completed, 3=cancelled"
    )
    winner: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
