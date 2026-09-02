"""
Traffic synchronization service.

Collects AmneziaWG traffic
and stores usage data.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.collectors.awg import AWGCollector
from backend.app.repositories.peer import PeerRepository
from backend.app.repositories.traffic import TrafficRepository
from backend.app.models.traffic import Traffic


class TrafficSyncService:
    """
    Sync AWG traffic into database.
    """


    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        self.collector = AWGCollector()

        self.peer_repository = PeerRepository(
            session
        )

        self.traffic_repository = TrafficRepository(
            session
        )


    async def sync(self) -> int:
        """
        Collect and save traffic.

        Returns:
            Number of synced peers.
        """

        records = self.collector.collect()

        synced = 0

        peers = await self.peer_repository.get_all()


        peer_map = {
            peer.address: peer
            for peer in peers
        }


        for item in records:

            address = item.get(
                "address"
            )


            peer = peer_map.get(
                address
            )


            if peer is None:
                continue


            upload = item.get(
                "upload_bytes",
                0,
            )

            download = item.get(
                "download_bytes",
                0,
            )


            # `awg show ... dump` reports cumulative counters.  Persist the
            # raw values on the peer and save only their deltas as billable
            # traffic records.
            upload_delta = max(0, upload - peer.last_upload_bytes)
            download_delta = max(0, download - peer.last_download_bytes)
            peer.last_upload_bytes = upload
            peer.last_download_bytes = download

            traffic = Traffic(
                peer_id=peer.id,
                upload_bytes=upload_delta,
                download_bytes=download_delta,
                total_bytes=(
                    upload_delta + download_delta
                ),
            )


            await self.traffic_repository.create(
                traffic
            )


            synced += 1


        return synced
