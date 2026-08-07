"""
Traffic background scheduler.

Runs traffic synchronization periodically.
"""

import asyncio

from backend.app.db.database import AsyncSessionLocal
from backend.app.services.traffic_sync import TrafficSyncService


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