"""
Activity Log Repository.

Database access layer for ActivityLog model.
"""

from backend.app.models.activity_log import ActivityLog

from .base import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLog]):
    """
    Repository for ActivityLog model.

    Handles database operations for activity log records.
    """

    def __init__(self) -> None:
        """Initialize ActivityLog repository."""
        super().__init__(ActivityLog)