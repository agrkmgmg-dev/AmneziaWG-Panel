import asyncio

from backend.app.db.database import AsyncSessionLocal
from backend.app.models.peer import Peer
from backend.app.services.peer import PeerService


async def create_test_peer() -> int:
    async with AsyncSessionLocal() as session:
        existing_peer = await session.execute(
            Peer.__table__.select().where(
                Peer.public_key == "STATUS_TEST_PUBLIC_KEY"
            )
        )

        row = existing_peer.first()

        if row is not None:
            peer = await session.get(Peer, row.id)

            if peer is not None:
                await session.delete(peer)
                await session.commit()

        peer = Peer(
            user_id=1,
            name="status-test-peer",
            public_key="STATUS_TEST_PUBLIC_KEY",
            private_key="STATUS_TEST_PRIVATE_KEY",
            address="10.10.0.99/32",
            is_active=True,
        )

        session.add(peer)

        await session.commit()
        await session.refresh(peer)

        return peer.id


def test_peer_enable_disable():
    async def run_test():
        peer_id = await create_test_peer()

        try:
            async with AsyncSessionLocal() as session:
                service = PeerService(session)

                # Disable
                disabled = await service.disable(peer_id)

                assert disabled is not None
                assert disabled.is_active is False

                # Enable
                enabled = await service.enable(peer_id)

                assert enabled is not None
                assert enabled.is_active is True

        finally:
            # Cleanup
            async with AsyncSessionLocal() as session:
                peer = await session.get(Peer, peer_id)

                if peer is not None:
                    await session.delete(peer)
                    await session.commit()

    asyncio.run(run_test())