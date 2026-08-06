from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.peer import Peer
from backend.app.repositories.base import BaseRepository


class PeerRepository(BaseRepository[Peer]):
    """
    Repository for Peer model.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=Peer)

    async def get_by_name(
        self,
        name: str,
    ) -> Peer | None:
        result = await self.session.execute(
            select(Peer).where(Peer.name == name)
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[Peer]:
        result = await self.session.execute(
            select(Peer).where(Peer.user_id == user_id)
        )

        return list(result.scalars().all())

    async def get_active(
        self,
    ) -> list[Peer]:
        result = await self.session.execute(
            select(Peer).where(Peer.is_active.is_(True))
        )

        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: int,
    ) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Peer)
            .where(Peer.user_id == user_id)
        )

        return result.scalar_one()