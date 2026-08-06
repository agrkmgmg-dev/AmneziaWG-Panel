"""
Traffic service layer.

Contains business logic related to peer traffic records.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.traffic import Traffic
from backend.app.repositories.traffic import TrafficRepository
from backend.app.schemas.traffic import TrafficCreate, TrafficResponse

from backend.app.services.base import BaseService


class TrafficService(BaseService):
    """
    Service class for Traffic operations.

    Responsibilities:
        - Handle traffic business logic.
        - Manage database transactions.
        - Coordinate with TrafficRepository.

    Traffic calculation and monitoring logic
    are intentionally handled outside this service.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize TrafficService.

        Args:
            session: Async SQLAlchemy database session.
        """
        super().__init__(session)

        self.repository = TrafficRepository(session)

    async def get_by_id(
        self,
        traffic_id: int,
    ) -> TrafficResponse | None:
        """
        Get traffic record by ID.

        Args:
            traffic_id: Traffic record primary key.

        Returns:
            TrafficResponse if found, otherwise None.
        """

        traffic = await self.repository.get_by_id(traffic_id)

        if traffic is None:
            return None

        return TrafficResponse.model_validate(traffic)

    async def get_all(self) -> list[TrafficResponse]:
        """
        Get all traffic records.

        Returns:
            List of traffic records.
        """

        traffics = await self.repository.get_all()

        return [
            TrafficResponse.model_validate(traffic)
            for traffic in traffics
        ]

    async def create(
        self,
        data: TrafficCreate,
    ) -> TrafficResponse:
        """
        Create traffic record.

        Args:
            data: Traffic creation schema.

        Returns:
            Created traffic response schema.
        """

        traffic = Traffic(
            peer_id=data.peer_id,
            download=data.download,
            upload=data.upload,
        )

        traffic = await self.repository.create(traffic)

        await self.commit()

        await self.refresh(traffic)

        return TrafficResponse.model_validate(traffic)

    async def delete(
        self,
        traffic_id: int,
    ) -> bool:
        """
        Delete traffic record by ID.

        Args:
            traffic_id: Traffic record primary key.

        Returns:
            True if deleted, otherwise False.
        """

        traffic = await self.repository.get_by_id(traffic_id)

        if traffic is None:
            return False

        await self.repository.delete(traffic)

        await self.commit()

        return True