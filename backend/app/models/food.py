"""Food model."""

from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Food(Base):
    """Food item, either from the built-in database, OpenFoodFacts, or user-created."""

    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    calories: Mapped[float] = mapped_column(Float, nullable=False, comment="calories per 100g")
    protein: Mapped[float] = mapped_column(Float, nullable=True, comment="protein per 100g")
    carbs: Mapped[float] = mapped_column(Float, nullable=True, comment="carbohydrate per 100g")
    fat: Mapped[float] = mapped_column(Float, nullable=True, comment="fat per 100g")
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    creator_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
