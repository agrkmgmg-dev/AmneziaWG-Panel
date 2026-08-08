"""
Authentication API router.

Provides:

- User login
- Refresh token
- Current authenticated user
- Logout / token revocation
"""

import jwt

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.dependencies import (
    get_auth_service,
)

from backend.app.core.dependencies import (
    get_current_user,
    require_active_user,
)

from backend.app.core.jwt import (
    decode_token,
)

from backend.app.db.database import (
    get_db,
)

from backend.app.models.user import User

from backend.app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)

from backend.app.services.auth import (
    AuthService,
)

from backend.app.services.token_revocation import (
    TokenRevocationService,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.
    """

    user = await service.authenticate(
        data.username,
        data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return TokenResponse(
        **service.create_tokens(user.id)
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Create new access and refresh tokens
    using a valid refresh token.
    """

    try:
        payload = decode_token(
            data.refresh_token
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None

    token_type = payload.get("type")

    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    subject = payload.get("sub")

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(subject)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        ) from None

    user = await service.repository.get_by_id(
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return TokenResponse(
        **service.create_tokens(user.id)
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
async def get_me(
    user: User = Depends(require_active_user),
) -> CurrentUserResponse:
    """
    Return the currently authenticated user.
    """

    return CurrentUserResponse.model_validate(
        user
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    token: str = Depends(oauth2_scheme),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """
    Revoke the current access token.

    After logout, the current JWT cannot be reused.
    """

    try:
        payload = decode_token(token)

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from None

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    jti = payload.get("jti")
    exp = payload.get("exp")

    if jti is None or exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    expires_at = datetime.fromtimestamp(
        exp,
        tz=timezone.utc,
    )

    service = TokenRevocationService(
        session
    )

    await service.revoke(
        jti=jti,
        expires_at=expires_at,
    )

    return None