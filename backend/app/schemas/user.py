"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: str | None = None
    avatar: str | None = None
    gender: int | None = Field(default=None, ge=0, le=1)
    height: float | None = Field(default=None, gt=0)
    age: int | None = Field(default=None, gt=0)
    target_weight: float | None = Field(default=None, gt=0)
    daily_calorie_goal: int | None = Field(default=None, gt=0)


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user data returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    gender: int | None = None
    height: float | None = None
    age: int | None = None
    target_weight: float | None = None
    daily_calorie_goal: int | None = None
    created_at: datetime | None = None


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    nickname: str | None = None
    avatar: str | None = None
    gender: int | None = Field(default=None, ge=0, le=1)
    height: float | None = Field(default=None, gt=0)
    age: int | None = Field(default=None, gt=0)
    target_weight: float | None = Field(default=None, gt=0)
    daily_calorie_goal: int | None = Field(default=None, gt=0)


class TokenResponse(BaseModel):
    """Schema for the JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
