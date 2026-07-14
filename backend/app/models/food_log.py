"""FoodLog model."""

from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FoodLog(Base):
    """A logged food entry for a user's meal."""

    __tablename__ = "food_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    food_id: Mapped[int] = mapped_column(Integer, ForeignKey("foods.id"), nullable=False)
    meal_type: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="0=breakfast, 1=lunch, 2=dinner, 3=snack"
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False, comment="amount in grams")
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein: Mapped[float] = mapped_column(Float, nullable=True)
    carbs: Mapped[float] = mapped_column(Float, nullable=True)
    fat: Mapped[float] = mapped_column(Float, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
