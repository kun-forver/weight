"""WeightLog model."""

from datetime import datetime

from sqlalchemy import Integer, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WeightLog(Base):
    """A daily weight measurement log."""

    __tablename__ = "weight_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False, comment="body weight in kg")
    body_fat: Mapped[float | None] = mapped_column(Float, nullable=True, comment="body fat percentage")
    muscle: Mapped[float | None] = mapped_column(Float, nullable=True, comment="muscle mass in kg")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
