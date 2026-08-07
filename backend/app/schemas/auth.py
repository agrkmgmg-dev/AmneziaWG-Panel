"""
Authentication schemas.

Contains request and response models
for JWT authentication flow.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    User login request.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
    )

    password: str = Field(
        ...,
        min_length=6,
    )


class TokenResponse(BaseModel):
    """
    JWT token response.
    """

    access_token: str

    refresh_token: str

    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Refresh token request.
    """

    refresh_token: str


class CurrentUserResponse(BaseModel):
    """
    Current authenticated user response.
    """

    id: int

    username: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }