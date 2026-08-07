"""
Usage limit service.

Handles peer traffic usage calculation
and limit checking.
"""

from backend.app.repositories.traffic import TrafficRepository


class UsageLimitService:
    """
    Manage peer traffic limits.
    """

    def __init__(
        self,
        traffic_repository: TrafficRepository,
    ) -> None:

        self.traffic_repository = traffic_repository


    async def get_usage(
        self,
        peer,
    ) -> int:
        """
        Return used bytes.
        """

        return await self.traffic_repository.get_total_traffic(
            peer.id
        )


    async def get_percent(
        self,
        peer,
    ) -> int:
        """
        Return usage percentage.
        """

        if not peer.traffic_limit_bytes:
            return 0


        used = await self.get_usage(peer)


        percent = (
            used * 100
        ) // peer.traffic_limit_bytes


        return min(percent, 100)


    async def is_exceeded(
        self,
        peer,
    ) -> bool:
        """
        Check if limit exceeded.
        """

        if peer.traffic_limit_bytes is None:
            return False


        used = await self.get_usage(peer)


        return used >= peer.traffic_limit_bytes


    async def get_status(
        self,
        peer,
    ) -> str:
        """
        Return usage status.
        """

        if peer.traffic_limit_bytes is None:
            return "بدون محدودیت"


        if await self.is_exceeded(peer):
            return "🔴 حجم تمام شده"


        percent = await self.get_percent(peer)


        if percent >= 80:
            return "🟡 نزدیک سقف"


        return "🟢 OK"


    async def get_display(
        self,
        peer,
    ) -> str:
        """
        Return human readable usage.
        """

        if peer.traffic_limit_bytes is None:
            return "بدون محدودیت"


        used = await self.get_usage(peer)

        percent = await self.get_percent(peer)


        return (
            f"{used} / "
            f"{peer.traffic_limit_bytes}"
            f" ({percent}%)"
        )