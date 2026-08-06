"""
Peer service layer.

Contains business logic related to WireGuard peers.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.peer import Peer
from backend.app.repositories.peer import PeerRepository
from backend.app.schemas.peer import PeerCreate, PeerResponse

from backend.app.services.base import BaseService


class PeerService(BaseService):
    """
    Service class for Peer operations.

    Responsibilities:
        - Handle peer business logic.
        - Manage transactions.
        - Coordinate with PeerRepository.

    Network configuration logic is intentionally
    handled outside this service.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize PeerService.

        Args:
            session: Async SQLAlchemy database session.
        """
        super().__init__(session)

        self.repository = PeerRepository(session)

    async def get_by_id(
        self,
        peer_id: int,
    ) -> PeerResponse | None:
        """
        Get peer by ID.

        Args:
            peer_id: Peer primary key.

        Returns:
            PeerResponse if peer exists, otherwise None.
        """

        peer = await self.repository.get_by_id(peer_id)

        if peer is None:
            return None

        return PeerResponse.model_validate(peer)

    async def get_all(self) -> list[PeerResponse]:
        """
        Get all peers.

        Returns:
            List of peers.
        """

        peers = await self.repository.get_all()

        return [
            PeerResponse.model_validate(peer)
            for peer in peers
        ]

    async def create(
        self,
        data: PeerCreate,
    ) -> PeerResponse:
        """
        Create new peer.

        Args:
            data: Peer creation schema.

        Returns:
            Created peer response schema.
        """

        peer = Peer(
            name=data.name,
            address=data.address,
            expires_at=data.expires_at,
        )

        peer = await self.repository.create(peer)

        await self.commit()

        await self.refresh(peer)

        return PeerResponse.model_validate(peer)

    async def delete(
        self,
        peer_id: int,
    ) -> bool:
        """
        Delete peer by ID.

        Args:
            peer_id: Peer primary key.

        Returns:
            True if deleted, otherwise False.
        """

        peer = await self.repository.get_by_id(peer_id)

        if peer is None:
            return False

        await self.repository.delete(peer)

        await self.commit()

        return True