"""
Dashboard service layer.

Provides statistics for admin dashboard.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.user import UserRepository
from backend.app.repositories.peer import PeerRepository
from backend.app.repositories.traffic import TrafficRepository
from backend.app.repositories.activity_log import ActivityLogRepository


class DashboardService:
    """
    Service for admin dashboard statistics.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.user_repository = UserRepository(session)
        self.peer_repository = PeerRepository(session)
        self.traffic_repository = TrafficRepository(session)
        self.activity_log_repository = ActivityLogRepository(session)

    async def get_users_count(self) -> int:
        """
        Return total users count.
        """

        return await self.user_repository.count()

    async def get_peers_count(self) -> int:
        """
        Return total peers count.
        """

        return await self.peer_repository.count()

    async def get_traffic_count(self) -> int:
        """
        Return total traffic records count.
        """

        return await self.traffic_repository.count()

    async def get_logs_count(self) -> int:
        """
        Return total activity logs count.
        """

        return await self.activity_log_repository.count()

    async def get_dashboard_stats(self) -> dict[str, int]:
        """
        Return all dashboard statistics.
        """

        return {
            "users_count": await self.get_users_count(),
            "peers_count": await self.get_peers_count(),
            "traffic_count": await self.get_traffic_count(),
            "logs_count": await self.get_logs_count(),
        }