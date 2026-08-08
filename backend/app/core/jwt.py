"""
JWT authentication utilities.

Provides:

- Access token creation
- Refresh token creation
- Token decoding and validation
- Unique JWT identifiers (JTI)
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt

from backend.app.core.config import settings


ALGORITHM = "HS256"


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    """
    Create a JWT token.

    Args:
        subject: Token subject, normally the user ID.
        token_type: Token type (access or refresh).
        expires_delta: Token lifetime.

    Returns:
        Encoded JWT token.
    """

    now = datetime.now(timezone.utc)

    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create an access token.
    """

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    return _create_token(
        subject=subject,
        token_type="access",
        expires_delta=expires_delta,
    )


def create_refresh_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a refresh token.
    """

    if expires_delta is None:
        expires_delta = timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=expires_delta,
    )


def decode_token(
    token: str,
) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Raises:
        jwt.InvalidTokenError:
            If the token is invalid or expired.

    Returns:
        Decoded JWT payload.
    """

    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM],
    )