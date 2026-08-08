"""
Token revocation repository.

Handles persistence and lookup of revoked JWT tokens.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.token_revocation import TokenRevocation
from backend.app.repositories.base import BaseRepository


class TokenRevocationRepository(BaseRepository):
    """
    Repository for revoked JWT tokens.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            TokenRevocation,
        )

    async def get_by_jti(
        self,
        jti: str,
    ) -> TokenRevocation | None:
        """
        Get revoked token by JTI.
        """

        result = await self.session.execute(
            select(TokenRevocation).where(
                TokenRevocation.jti == jti
            )
        )

        return result.scalar_one_or_none()

    async def is_revoked(
        self,
        jti: str,
    ) -> bool:
        """
        Check whether a JWT has been revoked.
        """

        token = await self.get_by_jti(jti)

        return token is not None