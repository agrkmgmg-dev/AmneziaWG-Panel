"""
Admin peer service.

Provides peer management operations used by the
server-side Admin Panel.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.peer import Peer
from backend.app.repositories.peer import PeerRepository
from backend.app.repositories.traffic import TrafficRepository

from backend.app.services.expiration import ExpirationService
from backend.app.services.ip_manager import IPManagerService
from backend.app.services.key_generator import KeyGeneratorService
from backend.app.services.usage_limit import UsageLimitService


class AdminPeerService:
    """
    Service for admin peer management.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

        self.peer_repository = PeerRepository(
            session
        )

        self.usage_service = UsageLimitService(
            TrafficRepository(session)
        )

    async def _attach_status(
        self,
        peer: Peer,
    ) -> Peer:
        """
        Attach calculated statuses.
        """

        peer.status = ExpirationService.get_status(
            peer
        )

        peer.usage_status = (
            await self.usage_service.get_status(peer)
        )

        peer.usage_display = (
            await self.usage_service.get_display(peer)
        )

        return peer

    async def get_peers(
        self,
    ) -> list[Peer]:
        """
        Return all peers with calculated status.
        """

        peers = await self.peer_repository.get_all_with_users()

        for peer in peers:
            await self._attach_status(peer)

        return peers

    async def get_peer(
        self,
        peer_id: int,
    ) -> Peer | None:
        """
        Return one peer with calculated status.
        """

        peer = await self.peer_repository.get_by_id(
            peer_id
        )

        if peer is not None:
            await self._attach_status(peer)

        return peer

    async def create_peer(
        self,
        user_id: int,
        name: str,
        expires_at=None,
        traffic_limit_bytes=None,
    ) -> Peer:
        """
        Create a peer with automatic keys and IP.
        """

        existing = await self.peer_repository.get_by_user(user_id)
        if existing:
            raise ValueError(
                "Each user is limited to one VPN device"
            )

        key_service = KeyGeneratorService()

        ip_service = IPManagerService(
            self.peer_repository
        )

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
            traffic_limit_bytes=traffic_limit_bytes,
            is_active=True,
        )

        peer = await self.peer_repository.create(peer)

        await self.session.commit()
        await self.session.refresh(peer)

        return peer

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

        if peer is None:
            return False

        await self.peer_repository.delete(peer)

        await self.session.commit()

        return True
