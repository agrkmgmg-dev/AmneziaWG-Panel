"""
Admin peer service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.peer import Peer
from backend.app.repositories.peer import PeerRepository
from backend.app.services.ip_manager import IPManagerService
from backend.app.services.key_generator import KeyGeneratorService


class AdminPeerService:
    """
    Service for admin peer management.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        self.peer_repository = PeerRepository(session)

    async def get_peers(
        self,
    ) -> list[Peer]:

        return await self.peer_repository.get_all_with_users()

    async def get_peer(
        self,
        peer_id: int,
    ) -> Peer | None:

        return await self.peer_repository.get_by_id(peer_id)

    async def create_peer(
        self,
        user_id: int,
        name: str,
        expires_at=None,
    ) -> Peer:
        """
        Create peer with automatic keys and IP.
        """

        key_service = KeyGeneratorService()
        ip_service = IPManagerService(self.peer_repository)

        private_key, public_key = (
            key_service.generate_keypair()
        )

        address = await ip_service.get_next_ip()

        peer = Peer(
            user_id=user_id,
            name=name,
            public_key=public_key,
            private_key=private_key,
            address=address,
            expires_at=expires_at,
            is_active=True,
        )

        return await self.peer_repository.create(peer)

    async def delete_peer(
        self,
        peer_id: int,
    ) -> bool:

        peer = await self.peer_repository.get_by_id(peer_id)

        if peer is None:
            return False

        await self.peer_repository.delete(peer)

        return True