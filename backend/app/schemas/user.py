"""User schemas."""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Username: 6-8 chars, starts with lowercase letter, followed by lowercase/digits/hyphens
USERNAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]{5,7}$")

# Password: at least 8 chars, must contain at least 2 of: uppercase, lowercase, digits, special chars
SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;:,.<>?/~")


def validate_password(password: str) -> str:
    """Validate password complexity: at least 8 chars, at least 2 character types."""
    if len(password) < 8:
        raise ValueError("密码至少8位")
    types = 0
    if any(c.isupper() for c in password):
        types += 1
    if any(c.islower() for c in password):
        types += 1
    if any(c.isdigit() for c in password):
        types += 1
    if any(c in SPECIAL_CHARS for c in password):
        types += 1
    if types < 2:
        raise ValueError("密码必须包含大写字母、小写字母、数字、特殊字符中的至少两种")
    return password


class SendCodeRequest(BaseModel):
    """Schema for requesting a verification code."""
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class UserCreate(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=6, max_length=8)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8, max_length=128)
    verification_code: str = Field(..., min_length=6, max_length=6)
    nickname: str | None = None
    avatar: str | None = None
    gender: int | None = Field(default=None, ge=0, le=1)
    height: float | None = Field(default=None, gt=0)
    age: int | None = Field(default=None, gt=0)
    target_weight: float | None = Field(default=None, gt=0)
    daily_calorie_goal: int | None = Field(default=None, gt=0)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not USERNAME_PATTERN.match(v):
            raise ValueError("用户名6-8位，小写字母开头，只能包含小写字母、数字和连字符")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user data returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    nickname: str | None = None
    avatar: str | None = None
    gender: int | None = None
    height: float | None = None
    age: int | None = None
    target_weight: float | None = None
    daily_calorie_goal: int | None = None
    role: str = "user"
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


class FriendshipResponse(BaseModel):
    """Schema for a friend in the friends list."""

    id: int  # friendship ID
    friend_id: int
    friend_name: str
    friend_avatar: str | None = None
    status: str  # "accepted" or "pending"


class ForgotPasswordRequest(BaseModel):
    """Schema for requesting a password reset email."""
    email: str


class ResetPasswordRequest(BaseModel):
    """Schema for resetting a password using a token."""
    token: str


class ChangePasswordRequest(BaseModel):
    """Schema for changing password from settings."""
    old_password: str
    new_password: str

