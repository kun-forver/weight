"""PK battle schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PKCreate(BaseModel):
    """Schema for creating a PK battle."""

    name: str = Field(..., min_length=1, max_length=100)
    user_b: int = Field(..., description="ID of the opponent")
    end_date: date
    target_a: float = Field(..., gt=0, description="target weight for the creator in kg")
    target_b: float = Field(..., gt=0, description="target weight for the opponent in kg")
    reward: str | None = None


class PKResponse(BaseModel):
    """Schema for a PK battle returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_a: int
    user_b: int
    start_date: date
    end_date: date
    target_a: float
    target_b: float
    start_weight_a: float | None = None
    start_weight_b: float | None = None
    reward: str | None = None
    status: int
    winner: int | None = None
    created_at: datetime

    # Extra display fields
    user_a_nickname: str | None = None
    user_b_nickname: str | None = None
    user_a_avatar: str | None = None
    user_b_avatar: str | None = None


class PKHistoryItem(BaseModel):
    """Schema for a PK battle history item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_a: int
    user_b: int
    start_date: date
    end_date: date
    target_a: float
    target_b: float
    start_weight_a: float | None = None
    start_weight_b: float | None = None
    reward: str | None = None
    status: int
    winner: int | None = None
    created_at: datetime

    user_a_nickname: str | None = None
    user_b_nickname: str | None = None


class PKPlayerDetails(BaseModel):
    """Schema for user details inside an active PK battle."""
    id: int
    name: str
    avatar: str | None = None
    score: float
    pct: float


class PKDetailsResponse(BaseModel):
    """Schema for detailed active PK battle returned to the client."""
    id: int
    name: str
    status: str
    reward: str | None = None
    days_total: int
    days_elapsed: int
    leader: int | None = None
    user_a: PKPlayerDetails
    user_b: PKPlayerDetails


class PKHistoryResponse(BaseModel):
    """Schema for a PK battle history item returned to the client."""
    id: int
    name: str
    start_date: date
    end_date: date
    result: str  # "win", "lose", "draw"
    rival_name: str
    my_score: float
    rival_score: float
