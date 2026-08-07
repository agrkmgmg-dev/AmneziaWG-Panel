"""
IP Manager Service.
"""

from backend.app.services.ip_pool import IPPoolService


class IPManagerService:
    """
    Manage peer IP allocation.
    """

    def __init__(
        self,
        peer_repository,
    ) -> None:

        self.peer_repository = peer_repository

        self.pool = IPPoolService(
            subnet="10.0.0.0/24",
            server_ip="10.0.0.1",
        )


    async def get_next_ip(self) -> str:
        """
        Return next available IP.
        """

        peers = await self.peer_repository.get_all()

        used_ips = [
            peer.address
            for peer in peers
            if peer.address
        ]

        return self.pool.get_next_ip(
            used_ips
        )