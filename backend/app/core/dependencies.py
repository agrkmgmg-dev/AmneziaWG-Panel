"""
Authentication dependencies.

Provides:
- Current authenticated user
- Active user validation
- JWT token validation
- Token revocation checking
- Peer ownership/access validation
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.jwt import decode_token
from backend.app.db.database import get_db
from backend.app.models.peer import Peer
from backend.app.models.user import User
from backend.app.repositories.peer import PeerRepository
from backend.app.repositories.user import UserRepository
from backend.app.services.token_revocation import (
    TokenRevocationService,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from JWT.

    Validates:
    - Token signature
    - Token expiration
    - Token type
    - Token JTI
    - Token revocation status
    - User existence
    """

    try:
        payload = decode_token(token)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if user_id is None or jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    revocation_service = TokenRevocationService(session)

    if await revocation_service.is_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id_int = int(user_id)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    repository = UserRepository(session)

    user = await repository.get_by_id(user_id_int)

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
    Ensure the authenticated user is active.
    """

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def require_peer_access(
    peer_id: int,
    current_user: User = Depends(require_active_user),
    session: AsyncSession = Depends(get_db),
) -> Peer:
    """
    Ensure the authenticated user has access to a peer.

    Superusers can access all peers.
    Regular users can access only their own peers.
    """

    repository = PeerRepository(session)

    peer = await repository.get_by_id(peer_id)

    if peer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peer not found",
        )

    if current_user.is_superuser:
        return peer

    if peer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this peer",
        )

    return peer
