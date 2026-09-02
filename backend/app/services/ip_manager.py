"""
IP Manager Service.
"""

from backend.app.services.ip_pool import IPPoolService
from backend.app.collectors.awg import AWGCollector
from pathlib import Path


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

        used_ips = {
            peer.address
            for peer in peers
            if peer.address
        }

        # The database may not contain peers created by the original
        # Amnezia installation. Reserve addresses reported by live AWG too,
        # otherwise a newly generated config can collide with an old peer.
        try:
            collector = AWGCollector()
            live_ips = (
                {
                    item["address"]
                    for item in collector.collect()
                    if item.get("address")
                }
                if not collector.mock_mode
                else set()
            )
            used_ips.update(live_ips)
            # Existing Amnezia installations use 10.8.1.0/24. Keep the
            # legacy 10.0.0.0/24 default for isolated tests/dev instances,
            # but allocate from the live network in production.
            if any(ip.startswith("10.8.1.") for ip in live_ips) or Path(
                "/run/amneziawg-panel/awg.sock"
            ).exists():
                self.pool = IPPoolService(
                    subnet="10.8.1.0/24",
                    server_ip="10.8.1.1",
                )
        except Exception:
            # Allocation must remain available in development/test mode when
            # the AWG binary or control socket is unavailable.
            pass

        return self.pool.get_next_ip(
            list(used_ips)
        )
