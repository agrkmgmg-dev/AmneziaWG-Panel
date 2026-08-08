"""
Traffic service layer.

Contains business logic related to traffic records.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.traffic import Traffic
from backend.app.repositories.traffic import TrafficRepository
from backend.app.schemas.traffic import (
    TrafficCreate,
    TrafficResponse,
    TrafficSummaryResponse,
)

from backend.app.services.base import BaseService


class TrafficService(BaseService):
    """
    Service class for Traffic operations.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        repository = TrafficRepository(session)

        super().__init__(
            session=session,
            repository=repository,
        )

        self.repository = repository

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
            TrafficResponse.model_validate(record)
            for record in records
        ]

    async def get_by_peer(
        self,
        peer_id: int,
    ) -> list[TrafficResponse]:
        """
        Get all traffic records for a peer.
        """

        records = await self.repository.get_by_peer(
            peer_id
        )

        return [
            TrafficResponse.model_validate(record)
            for record in records
        ]

    async def create(
        self,
        data: TrafficCreate,
    ) -> TrafficResponse:
        """
        Create a traffic record.

        Total bytes are calculated from upload
        and download values.
        """

        total_bytes = (
            data.upload_bytes
            + data.download_bytes
        )

        traffic = Traffic(
            peer_id=data.peer_id,
            upload_bytes=data.upload_bytes,
            download_bytes=data.download_bytes,
            total_bytes=total_bytes,
        )

        traffic = await self.repository.create(
            traffic
        )

        await self.commit()
        await self.refresh(traffic)

        return TrafficResponse.model_validate(
            traffic
        )

    async def get_summary(
        self,
        peer_id: int,
    ) -> TrafficSummaryResponse:
        """
        Get aggregated traffic usage for a peer.
        """

        total_upload = (
            await self.repository
            .get_total_upload_by_peer(peer_id)
        )

        total_download = (
            await self.repository
            .get_total_download_by_peer(peer_id)
        )

        total = (
            await self.repository
            .get_total_by_peer(peer_id)
        )

        return TrafficSummaryResponse(
            peer_id=peer_id,
            total_upload_bytes=total_upload,
            total_download_bytes=total_download,
            total_bytes=total,
        )

    async def get_latest(
        self,
        peer_id: int,
    ) -> TrafficResponse | None:
        """
        Get the latest traffic record for a peer.
        """

        traffic = (
            await self.repository
            .get_latest_by_peer(peer_id)
        )

        if traffic is None:
            return None

        return TrafficResponse.model_validate(
            traffic
        )

    async def count_by_peer(
        self,
        peer_id: int,
    ) -> int:
        """
        Count traffic records for a peer.
        """

        return await self.repository.count_by_peer(
            peer_id
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

        await self.repository.delete(traffic)

        await self.commit()

        return True
