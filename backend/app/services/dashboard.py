"""
Dashboard service layer.

Provides statistics and recent activities
for admin dashboard.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.user import UserRepository
from backend.app.repositories.peer import PeerRepository
from backend.app.repositories.traffic import TrafficRepository
from backend.app.repositories.activity_log import ActivityLogRepository
from backend.app.services.ip_pool import IPPoolService


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


    async def get_recent_logs(
        self,
        limit: int = 10,
    ):
        """
        Return latest activity logs.
        """

        return await self.activity_log_repository.get_latest(
            limit=limit
        )


    async def get_dashboard_stats(self) -> dict:
        """
        Return dashboard statistics and recent logs.
        """

        peers = await self.peer_repository.get_all()

        used_ips = [
            peer.address
            for peer in peers
            if peer.address
        ]

        pool = IPPoolService(
            subnet="10.0.0.0/24",
            server_ip="10.0.0.1",
        )

        ip_stats = pool.get_statistics(
            used_ips
        )

        return {
            "users_count": await self.get_users_count(),
            "peers_count": await self.get_peers_count(),
            "traffic_count": await self.get_traffic_count(),
            "logs_count": await self.get_logs_count(),
            "recent_logs": await self.get_recent_logs(),
            "ip_pool": ip_stats,
        }