"""
Traffic background scheduler.

Runs traffic synchronization periodically.
"""

import asyncio

from backend.app.db.database import AsyncSessionLocal
from backend.app.services.traffic_sync import TrafficSyncService
from backend.app.services.awg_manager import AWGManagerService
from backend.app.services.expiration import ExpirationService
from backend.app.services.usage_limit import UsageLimitService
from backend.app.repositories.traffic import TrafficRepository
from backend.app.repositories.peer import PeerRepository
from backend.app.core.config import settings


class TrafficScheduler:
    """
    Background traffic sync scheduler.
    """

    def __init__(
        self,
        interval: int = 60,
    ) -> None:
        self.interval = interval
        self.task = None
        self.running = False


    async def sync_loop(self):
        """
        Periodic traffic sync loop.
        """

        while self.running:

            try:
                async with AsyncSessionLocal() as session:

                    service = TrafficSyncService(
                        session
                    )

                    synced = await service.sync()

                    # Enforce time limits on the live interface, not only in
                    # the dashboard status. Expired peers are removed from
                    # AmneziaWG while their database record is retained.
                    manager = AWGManagerService()
                    usage = UsageLimitService(TrafficRepository(session))
                    for peer in await PeerRepository(session).get_all():
                        if peer.is_active and peer.rate_limit_mbps:
                            try:
                                manager.set_rate_limit(
                                    peer.address,
                                    peer.rate_limit_mbps,
                                )
                            except Exception:
                                pass
                        if peer.is_active and (
                            ExpirationService.is_expired(peer.expires_at)
                            or await usage.is_exceeded(peer)
                        ):
                            try:
                                manager.remove_peer(peer.public_key)
                            except Exception:
                                pass
                            peer.is_active = False

                    await session.commit()

                    print(
                        f"Traffic sync completed: {synced} peers"
                    )

            except Exception as e:

                print(
                    f"Traffic sync error: {e}"
                )


            await asyncio.sleep(
                self.interval
            )


    async def start(self):
        """
        Start scheduler.
        """

        if self.running:
            return

        self.running = True

        self.task = asyncio.create_task(
            self.sync_loop()
        )


    async def stop(self):
        """
        Stop scheduler.
        """

        self.running = False

        if self.task:
            self.task.cancel()
