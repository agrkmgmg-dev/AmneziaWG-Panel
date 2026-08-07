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
        """
        Return traffic records for peer.
        """

        result = await self.session.execute(
            select(Traffic)
            .where(
                Traffic.peer_id == peer_id
            )
            .order_by(
                Traffic.created_at.desc()
            )
        )

        return list(
            result.scalars().all()
        )


    async def get_total_upload(
        self,
        peer_id: int,
    ) -> int:
        """
        Return total upload bytes.
        """

        result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(
                        Traffic.upload_bytes
                    ),
                    0,
                )
            )
            .where(
                Traffic.peer_id == peer_id
            )
        )

        return result.scalar_one()


    async def get_total_download(
        self,
        peer_id: int,
    ) -> int:
        """
        Return total download bytes.
        """

        result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(
                        Traffic.download_bytes
                    ),
                    0,
                )
            )
            .where(
                Traffic.peer_id == peer_id
            )
        )

        return result.scalar_one()


    async def get_total_traffic(
        self,
        peer_id: int,
    ) -> int:
        """
        Return total traffic usage.
        """

        result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(
                        Traffic.upload_bytes
                        + Traffic.download_bytes
                    ),
                    0,
                )
            )
            .where(
                Traffic.peer_id == peer_id
            )
        )

        return result.scalar_one()


    async def count(self) -> int:
        """
        Count total traffic records.
        """

        result = await self.session.execute(
            select(
                func.count()
            )
            .select_from(
                Traffic
            )
        )

        return result.scalar_one()