"""
Traffic service layer.

Contains business logic related to peer traffic records
and usage limit monitoring.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.traffic import Traffic
from backend.app.repositories.traffic import TrafficRepository
from backend.app.schemas.traffic import (
    TrafficCreate,
    TrafficResponse,
)

from backend.app.services.base import BaseService


class TrafficService(BaseService):
    """
    Service class for Traffic operations.

    Responsibilities:
        - Handle traffic business logic.
        - Manage database transactions.
        - Create traffic records.
        - Calculate peer usage.
        - Check usage limits.
    """


    WARNING_PERCENT = 80


    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Initialize TrafficService.
        """

        super().__init__(
            session
        )

        self.repository = TrafficRepository(
            session
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

        traffics = await self.repository.get_all()

        return [
            TrafficResponse.model_validate(
                traffic
            )
            for traffic in traffics
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
            upload_bytes=data.upload_bytes,
            download_bytes=data.download_bytes,
            total_bytes=(
                data.upload_bytes
                +
                data.download_bytes
            ),
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


    async def get_usage(
        self,
        peer_id: int,
    ) -> dict:
        """
        Return total peer usage.
        """

        upload = await self.repository.get_total_upload(
            peer_id
        )

        download = await self.repository.get_total_download(
            peer_id
        )

        total = upload + download


        return {
            "peer_id": peer_id,

            "upload_bytes": upload,

            "download_bytes": download,

            "total_bytes": total,

            "upload_mb": round(
                upload / 1024 / 1024,
                2,
            ),

            "download_mb": round(
                download / 1024 / 1024,
                2,
            ),

            "total_mb": round(
                total / 1024 / 1024,
                2,
            ),
        }



    async def check_limit(
        self,
        peer_id: int,
        limit_bytes: int,
    ) -> dict:
        """
        Check traffic usage limit.
        """

        usage = await self.get_usage(
            peer_id
        )

        used = usage["total_bytes"]


        if used >= limit_bytes:

            status = "EXCEEDED"


        elif used >= (
            limit_bytes
            *
            self.WARNING_PERCENT
            /
            100
        ):

            status = "WARNING"


        else:

            status = "OK"


        return {
            **usage,

            "limit_bytes": limit_bytes,

            "remaining_bytes": max(
                limit_bytes - used,
                0,
            ),

            "status": status,
        }



    async def delete(
        self,
        traffic_id: int,
    ) -> bool:
        """
        Delete traffic record by ID.
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