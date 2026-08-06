"""
Activity Log Repository.

Database access layer for ActivityLog model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.activity_log import ActivityLog

from .base import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLog]):
    """
    Repository for ActivityLog model.

    Handles activity log database operations.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Initialize ActivityLog repository.
        """

        super().__init__(
            session=session,
            model=ActivityLog,
        )


    async def get_latest(
        self,
        limit: int = 10,
    ) -> list[ActivityLog]:
        """
        Return latest activity logs.
        """

        query = (
            select(ActivityLog)
            .order_by(
                ActivityLog.created_at.desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(query)

        return list(
            result.scalars().all()
        )