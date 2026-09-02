"""
Peer service layer.

Contains business logic related to AmneziaWG peers.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.peer import Peer
from backend.app.models.user import User
from backend.app.repositories.peer import PeerRepository
from backend.app.schemas.peer import (
    PeerCreate,
    PeerResponse,
    PeerUpdate,
)
from backend.app.services.base import BaseService
from backend.app.services.ip_manager import IPManagerService
from backend.app.services.key_generator import KeyGeneratorService
from backend.app.services.awg_manager import AWGManagerService
from backend.app.core.config import settings


class PeerService(BaseService):
    """
    Service class for Peer operations.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Initialize PeerService.
        """

        repository = PeerRepository(session)

        super().__init__(
            session=session,
            repository=repository,
        )

        self.repository = repository

        self.key_generator = KeyGeneratorService()

        self.ip_manager = IPManagerService(
            peer_repository=self.repository,
        )

    async def get_for_user(
        self,
        peer_id: int,
        current_user: User,
    ) -> Peer | None:
        """
        Get peer model if the current user has access.

        Superusers can access all peers.
        Regular users can access only their own peers.
        """

        peer = await self.repository.get_by_id(peer_id)

        if peer is None:
            return None

        if current_user.is_superuser:
            return peer

        if peer.user_id != current_user.id:
            return None

        return peer

    async def get_by_id(
        self,
        peer_id: int,
    ) -> PeerResponse | None:
        """
        Get peer by ID.
        """

        peer = await self.repository.get_by_id(peer_id)

        if peer is None:
            return None

        return PeerResponse.model_validate(peer)

    async def get_all(
        self,
    ) -> list[PeerResponse]:
        """
        Get all peers.
        """

        peers = await self.repository.get_all()

        return [
            PeerResponse.model_validate(peer)
            for peer in peers
        ]

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[PeerResponse]:
        """
        Get all peers belonging to a user.
        """

        peers = await self.repository.get_by_user(user_id)

        return [
            PeerResponse.model_validate(peer)
            for peer in peers
        ]

    async def create(
        self,
        data: PeerCreate,
    ) -> PeerResponse:
        """
        Create a new peer.

        Generates a real WireGuard key pair and
        automatically allocates an available IP address.
        """

        existing_peer = await self.repository.get_by_name(
            data.name
        )

        if existing_peer is not None:
            raise ValueError(
                "Peer name already exists"
            )

        private_key, public_key = (
            self.key_generator.generate_keypair()
        )
        preshared_key = self.key_generator.generate_preshared_key()

        address = data.address

        if not address:
            address = await self.ip_manager.get_next_ip()

        peer = Peer(
            user_id=data.user_id,
            name=data.name,
            address=address,
            expires_at=data.expires_at,
            private_key=private_key,
            public_key=public_key,
            preshared_key=preshared_key,
        )

        peer = await self.repository.create(peer)

        if settings.AWG_AUTO_SYNC:
            try:
                AWGManagerService().add_peer(
                    peer.public_key,
                    peer.address,
                    peer.preshared_key,
                )
            except Exception as exc:
                await self.repository.delete(peer)
                raise RuntimeError(
                    "VPN peer provisioning failed; no configuration was created"
                ) from exc

        return PeerResponse.model_validate(peer)

    async def update(
        self,
        peer_id: int,
        data: PeerUpdate,
    ) -> PeerResponse | None:
        """
        Update an existing peer.
        """

        peer = await self.repository.get_by_id(peer_id)

        if peer is None:
            return None

        if data.name is not None:
            existing_peer = await self.repository.get_by_name(
                data.name
            )

            if (
                existing_peer is not None
                and existing_peer.id != peer_id
            ):
                raise ValueError(
                    "Peer name already exists"
                )

            peer.name = data.name

        if data.is_active is not None:
            peer.is_active = data.is_active

        if data.expires_at is not None:
            peer.expires_at = data.expires_at

        await self.commit()
        await self.refresh(peer)

        return PeerResponse.model_validate(peer)

    async def enable(
        self,
        peer_id: int,
    ) -> PeerResponse | None:
        """
        Enable a peer.

        Sets the peer status to active.
        """

        peer = await self.repository.get_by_id(peer_id)

        if peer is None:
            return None

        peer.is_active = True

        await self.commit()
        await self.refresh(peer)

        return PeerResponse.model_validate(peer)

    async def disable(
        self,
        peer_id: int,
    ) -> PeerResponse | None:
        """
        Disable a peer.

        Sets the peer status to inactive.
        """

        peer = await self.repository.get_by_id(peer_id)

        if peer is None:
            return None

        peer.is_active = False

        await self.commit()
        await self.refresh(peer)

        return PeerResponse.model_validate(peer)

    async def delete(
        self,
        peer_id: int,
    ) -> bool:
        """
        Delete peer by ID.
        """

        peer = await self.repository.get_by_id(peer_id)

        if peer is None:
            return False

        if settings.AWG_AUTO_SYNC:
            try:
                AWGManagerService().remove_peer(peer.public_key)
            except Exception:
                pass

        await self.repository.delete(peer)

        await self.commit()

        return True
