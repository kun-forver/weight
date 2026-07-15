"""Food and food log schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FoodSearch(BaseModel):
    """Schema for a food search query."""

    query: str = Field(..., min_length=1)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class FoodResponse(BaseModel):
    """Schema for food data returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    category: str | None = None
    calories: float
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    is_custom: bool = False
    source: str = "local"  # "local" or "openfoodfacts"


class FoodLogCreate(BaseModel):
    """Schema for creating a food log entry."""

    food_id: int | None = None
    food_name: str | None = None  # For custom food not in DB
    meal_type: int = Field(..., ge=0, le=3, description="0=breakfast, 1=lunch, 2=dinner, 3=snack")
    amount: float = Field(..., gt=0, description="amount in grams")
    calories: float = Field(default=0, ge=0)
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None


class FoodLogResponse(BaseModel):
    """Schema for a food log entry returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    food_id: int | None = None
    food_name: str | None = None
    meal_type: int
    amount: float
    calories: float
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    logged_at: datetime


class FoodLogSummary(BaseModel):
    """Schema for daily food log summary (per meal type)."""

    meal_type: int
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    count: int
