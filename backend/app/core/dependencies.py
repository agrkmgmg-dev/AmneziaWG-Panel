"""
Authentication dependencies.

Provides:

- Current authenticated user
- Active user validation
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.jwt import decode_token
from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.repositories.user import UserRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    """

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id = int(user_id)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    repository = UserRepository(session)

    user = await repository.get_by_id(
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user


async def require_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Ensure authenticated user is active.
    """

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user