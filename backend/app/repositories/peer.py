"""
Peer Repository
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.peer import Peer
from backend.app.repositories.base import BaseRepository


class PeerRepository(BaseRepository[Peer]):
    """
    Repository for Peer model.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=Peer,
        )

    async def get_by_name(
        self,
        name: str,
    ) -> Peer | None:
        """
        Return peer by name.
        """

        result = await self.session.execute(
            select(Peer).where(
                Peer.name == name
            )
        )

        return result.scalar_one_or_none()


    async def get_by_user(
        self,
        user_id: int,
    ) -> list[Peer]:
        """
        Return peers by user.
        """

        result = await self.session.execute(
            select(Peer).where(
                Peer.user_id == user_id
            )
        )

        return list(
            result.scalars().all()
        )


    async def get_all_with_users(
        self,
    ) -> list[Peer]:
        """
        Return all peers with user relation.
        """

        result = await self.session.execute(
            select(Peer)
            .options(
                selectinload(Peer.user)
            )
        )

        return list(
            result.scalars().all()
        )


    async def get_active(
        self,
    ) -> list[Peer]:
        """
        Return active peers.
        """

        result = await self.session.execute(
            select(Peer).where(
                Peer.is_active.is_(True)
            )
        )

        return list(
            result.scalars().all()
        )


    async def count_by_user(
        self,
        user_id: int,
    ) -> int:
        """
        Count peers by user.
        """

        result = await self.session.execute(
            select(func.count())
            .select_from(Peer)
            .where(
                Peer.user_id == user_id
            )
        )

        return result.scalar_one()


    async def count(
        self,
    ) -> int:
        """
        Count total peers.
        """

        result = await self.session.execute(
            select(func.count())
            .select_from(Peer)
        )

        return result.scalar_one()