"""
Admin peer service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.peer import Peer
from backend.app.repositories.peer import PeerRepository


class AdminPeerService:
    """
    Service for admin peer management.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        self.peer_repository = PeerRepository(
            session
        )
    async def get_peers(
        self,
    ) -> list[Peer]:
        """
        Return all peers with users.
        """

        return await self.peer_repository.get_all_with_users()

    async def get_peer(
        self,
        peer_id: int,
    ) -> Peer | None:
        """
        Return one peer.
        """

        return await self.peer_repository.get_by_id(
            peer_id
        )

    async def get_user_peers(
        self,
        user_id: int,
    ) -> list[Peer]:
        """
        Return peers for user.
        """

        return await self.peer_repository.get_by_user_id(
            user_id
        )

    async def create_peer(
        self,
        user_id: int,
        name: str,
        public_key: str,
        address: str,
        private_key: str | None = None,
        expires_at=None,
    ) -> Peer:
        """
        Create new peer.
        """

        peer = Peer(
            user_id=user_id,
            name=name,
            public_key=public_key,
            private_key=private_key,
            address=address,
            expires_at=expires_at,
            is_active=True,
        )

        return await self.peer_repository.create(
            peer
        )

    async def delete_peer(
        self,
        peer_id: int,
    ) -> bool:
        """
        Delete peer by ID.
        """

        peer = await self.peer_repository.get_by_id(
            peer_id
        )

        if not peer:
            return False

        await self.peer_repository.delete(
            peer
        )

        return True