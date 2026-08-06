"""
Activity Log Repository.

Database access layer for ActivityLog model.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.activity_log import ActivityLog
from backend.app.repositories.base import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLog]):
    """
    Repository for ActivityLog model.

    Handles database operations for activity log records.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session=session,
            model=ActivityLog,
        )

    async def count(self) -> int:
        """
        Count total activity logs.
        """

        result = await self.session.execute(
            select(func.count())
            .select_from(ActivityLog)
        )

        return result.scalar_one()