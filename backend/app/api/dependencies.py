"""
FastAPI dependency providers.

Provides database sessions and service instances.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import AsyncSessionLocal

from backend.app.services import (
    ActivityLogService,
    PeerService,
    TrafficService,
    UserService,
)

from backend.app.services.auth import AuthService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide async database session.
    """

    async with AsyncSessionLocal() as session:
        yield session


def get_user_service(
    session: AsyncSession = Depends(get_db),
) -> UserService:
    """
    Provide UserService instance.
    """

    return UserService(session)


def get_peer_service(
    session: AsyncSession = Depends(get_db),
) -> PeerService:
    """
    Provide PeerService instance.
    """

    return PeerService(session)


def get_traffic_service(
    session: AsyncSession = Depends(get_db),
) -> TrafficService:
    """
    Provide TrafficService instance.
    """

    return TrafficService(session)


def get_activity_log_service(
    session: AsyncSession = Depends(get_db),
) -> ActivityLogService:
    """
    Provide ActivityLogService instance.
    """

    return ActivityLogService(session)


def get_auth_service(
    session: AsyncSession = Depends(get_db),
) -> AuthService:
    """
    Provide AuthService instance.
    """

    return AuthService(session)