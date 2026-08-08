"""
Activity Log service layer.

Contains business logic related to activity logs.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.activity_log import ActivityLog
from backend.app.repositories.activity_log import ActivityLogRepository
from backend.app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogResponse,
)
from backend.app.services.base import BaseService


class ActivityLogService(BaseService):
    """
    Service class for Activity Log operations.

    Responsibilities:
        - Handle activity log business logic.
        - Coordinate with ActivityLogRepository.
        - Manage transactions.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Initialize ActivityLogService.
        """

        repository = ActivityLogRepository(session)

        super().__init__(
            session,
            repository,
        )

        self.repository = repository

    async def get_by_id(
        self,
        log_id: int,
    ) -> ActivityLogResponse | None:
        """
        Get activity log by ID.
        """

        log = await self.repository.get_by_id(log_id)

        if log is None:
            return None

        return ActivityLogResponse.model_validate(log)

    async def get_all(
        self,
    ) -> list[ActivityLogResponse]:
        """
        Get all activity logs.
        """

        logs = await self.repository.get_all()

        return [
            ActivityLogResponse.model_validate(log)
            for log in logs
        ]

    async def get_latest(
        self,
        limit: int = 10,
    ) -> list[ActivityLogResponse]:
        """
        Get latest activity logs.
        """

        logs = await self.repository.get_latest(limit)

        return [
            ActivityLogResponse.model_validate(log)
            for log in logs
        ]

    async def create(
        self,
        data: ActivityLogCreate,
    ) -> ActivityLogResponse:
        """
        Create activity log.
        """

        log = ActivityLog(
            user_id=data.user_id,
            action=data.action,
            description=data.description,
        )

        log = await self.repository.create(log)

        await self.commit()
        await self.refresh(log)

        return ActivityLogResponse.model_validate(log)

    async def delete(
        self,
        log_id: int,
    ) -> bool:
        """
        Delete activity log.
        """

        log = await self.repository.get_by_id(log_id)

        if log is None:
            return False

        await self.repository.delete(log)

        await self.commit()

        return True