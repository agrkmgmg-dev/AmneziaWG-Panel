"""
Traffic Repository

Database access layer for peer traffic records.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.traffic import Traffic
from backend.app.repositories.base import BaseRepository


class TrafficRepository(BaseRepository[Traffic]):
    """
    Repository for Traffic model.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session=session,
            model=Traffic,
        )

    async def get_by_peer(
        self,
        peer_id: int,
    ) -> list[Traffic]:

        result = await self.session.execute(
            select(Traffic)
            .where(Traffic.peer_id == peer_id)
            .order_by(Traffic.id)
        )

        return list(result.scalars().all())

    async def get_latest_by_peer(
        self,
        peer_id: int,
    ) -> Traffic | None:

        result = await self.session.execute(
            select(Traffic)
            .where(Traffic.peer_id == peer_id)
            .order_by(Traffic.id.desc())
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_total_upload_by_peer(
        self,
        peer_id: int,
    ) -> int:

        result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(Traffic.upload_bytes),
                    0,
                )
            )
            .where(Traffic.peer_id == peer_id)
        )

        return int(result.scalar_one())

    async def get_total_download_by_peer(
        self,
        peer_id: int,
    ) -> int:

        result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(Traffic.download_bytes),
                    0,
                )
            )
            .where(Traffic.peer_id == peer_id)
        )

        return int(result.scalar_one())

    async def get_total_by_peer(
        self,
        peer_id: int,
    ) -> int:

        result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(Traffic.total_bytes),
                    0,
                )
            )
            .where(Traffic.peer_id == peer_id)
        )

        return int(result.scalar_one())

    async def count_by_peer(
        self,
        peer_id: int,
    ) -> int:

        result = await self.session.execute(
            select(func.count())
            .select_from(Traffic)
            .where(Traffic.peer_id == peer_id)
        )

        return int(result.scalar_one())

    async def count(self) -> int:

        result = await self.session.execute(
            select(func.count())
            .select_from(Traffic)
        )

        return int(result.scalar_one())
