"""Weight log schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WeightCreate(BaseModel):
    """Schema for creating a weight log entry."""

    weight: float = Field(..., gt=0, description="body weight in kg")
    body_fat: float | None = Field(default=None, ge=0, le=100)
    muscle: float | None = Field(default=None, ge=0)
    note: str | None = None


class WeightResponse(BaseModel):
    """Schema for a weight log entry returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    weight: float
    body_fat: float | None = None
    muscle: float | None = None
    note: str | None = None
    logged_at: datetime


class WeightSummary(BaseModel):
    """Schema for weight summary."""

    latest_weight: float | None = None
    previous_weight: float | None = None
    change: float | None = None
    total_records: int = 0
    target_weight: float | None = None
    target_diff: float | None = None
