from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username",
    )


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password",
    )


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )

    is_active: bool | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str


class UserListResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    users: list[UserResponse]
    total: int
