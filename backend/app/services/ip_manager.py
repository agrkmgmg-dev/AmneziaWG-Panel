"""
Automatic IP Address Manager.
"""

from ipaddress import IPv4Address

from backend.app.repositories.peer import PeerRepository


class IPManagerService:
    """
    Allocate the first available WireGuard client IP.
    """

    def __init__(
        self,
        peer_repository: PeerRepository,
    ) -> None:
        self.peer_repository = peer_repository

    async def get_next_ip(self) -> str:
        """
        Return first free IP from 10.0.0.2/32
        """

        peers = await self.peer_repository.get_all()

        used = set()

        for peer in peers:
            if peer.address:
                ip = peer.address.split("/")[0]
                used.add(ip)

        for i in range(2, 255):
            ip = f"10.0.0.{i}"

            if ip not in used:
                return f"{ip}/32"

        raise ValueError("No free IP addresses available.")