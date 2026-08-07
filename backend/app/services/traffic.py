"""
Traffic service layer.

Contains business logic related to traffic records.
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
        - Coordinate with TrafficRepository.
        - Manage transactions.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Initialize TrafficService.
        """

        repository = TrafficRepository(session)

        super().__init__(
            session,
            repository,
        )

    async def get_by_id(
        self,
        traffic_id: int,
    ) -> TrafficResponse | None:
        """
        Get traffic record by ID.
        """

        traffic = await self.repository.get_by_id(
            traffic_id
        )

        if traffic is None:
            return None

        return TrafficResponse.model_validate(
            traffic
        )

    async def get_all(
        self,
    ) -> list[TrafficResponse]:
        """
        Get all traffic records.
        """

        records = await self.repository.get_all()

        return [
            TrafficResponse.model_validate(
                record
            )
            for record in records
        ]

    async def create(
        self,
        data: TrafficCreate,
    ) -> TrafficResponse:
        """
        Create traffic record.
        """

        traffic = Traffic(
            peer_id=data.peer_id,
            download_bytes=data.download_bytes,
            upload_bytes=data.upload_bytes,
        )

        traffic = await self.repository.create(
            traffic
        )

        await self.commit()

        await self.refresh(
            traffic
        )

        return TrafficResponse.model_validate(
            traffic
        )

    async def delete(
        self,
        traffic_id: int,
    ) -> bool:
        """
        Delete traffic record.
        """

        traffic = await self.repository.get_by_id(
            traffic_id
        )

        if traffic is None:
            return False

        await self.repository.delete(
            traffic
        )

        await self.commit()

        return True

    async def get_usage(
        self,
        peer_id: int,
    ) -> dict:
        """
        Return peer traffic usage.
        """

        return await self.repository.get_usage(
            peer_id
        )

    async def check_limit(
        self,
        peer_id: int,
        limit_bytes: int,
    ) -> dict:
        """
        Check peer traffic limit.
        """

        return await self.repository.check_limit(
            peer_id,
            limit_bytes,
        )