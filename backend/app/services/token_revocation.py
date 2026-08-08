"""
Token revocation service.

Handles JWT token revocation and blacklist checks.
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.token_revocation import TokenRevocation
from backend.app.repositories.token_revocation import (
    TokenRevocationRepository,
)
from backend.app.services.base import BaseService


class TokenRevocationService(BaseService):
    """
    Service responsible for JWT token revocation.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        repository = TokenRevocationRepository(session)

        super().__init__(
            session,
            repository,
        )

        self.repository = repository

    async def revoke(
        self,
        jti: str,
        expires_at: datetime,
    ) -> TokenRevocation:
        """
        Revoke a JWT token.

        Args:
            jti: Unique JWT identifier.
            expires_at: Token expiration timestamp.

        Returns:
            Created TokenRevocation record.
        """

        existing = await self.repository.get_by_jti(jti)

        if existing is not None:
            return existing

        token = TokenRevocation(
            jti=jti,
            expires_at=expires_at,
        )

        token = await self.repository.create(token)

        await self.commit()
        await self.refresh(token)

        return token

    async def is_revoked(
        self,
        jti: str,
    ) -> bool:
        """
        Check whether a JWT has been revoked.
        """

        return await self.repository.is_revoked(jti)