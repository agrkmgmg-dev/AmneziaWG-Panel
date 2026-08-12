import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.schemas.peer import PeerCreate
from backend.app.services.peer import PeerService


def _prepare_created_peer(peer, peer_id: int):
    """
    Simulate SQLAlchemy/database generated fields.
    """
    peer.id = peer_id

    if peer.is_active is None:
        peer.is_active = True

    now = datetime.now(timezone.utc)

    if peer.created_at is None:
        peer.created_at = now

    if peer.updated_at is None:
        peer.updated_at = now

    return peer


def test_peer_service_create_generates_keys_and_auto_assigns_ip():
    async def run_test():
        session = MagicMock()

        service = PeerService(session)

        service.repository.get_by_name = AsyncMock(
            return_value=None
        )

        service.repository.create = AsyncMock(
            side_effect=lambda peer: _prepare_created_peer(
                peer,
                1,
            )
        )

        service.commit = AsyncMock()
        service.refresh = AsyncMock()

        data = PeerCreate(
            user_id=1,
            name="integration-peer",
            address=None,
            expires_at=None,
        )

        with patch.object(
            service.key_generator,
            "generate_keypair",
            return_value=(
                "PRIVATE_KEY_TEST",
                "PUBLIC_KEY_TEST",
            ),
        ) as mock_keypair:

            with patch.object(
                service.ip_manager,
                "get_next_ip",
                new=AsyncMock(
                    return_value="10.0.0.2/32"
                ),
            ) as mock_ip:

                result = await service.create(data)

        assert result.id == 1
        assert result.name == "integration-peer"
        assert result.user_id == 1
        assert result.address == "10.0.0.2/32"
        assert result.public_key == "PUBLIC_KEY_TEST"
        assert result.is_active is True
        assert result.created_at is not None
        assert result.updated_at is not None

        mock_keypair.assert_called_once()
        mock_ip.assert_awaited_once()

        service.repository.create.assert_awaited_once()
        service.commit.assert_awaited_once()
        service.refresh.assert_awaited_once()

    asyncio.run(run_test())


def test_peer_service_create_uses_explicit_ip():
    async def run_test():
        session = MagicMock()

        service = PeerService(session)

        service.repository.get_by_name = AsyncMock(
            return_value=None
        )

        service.repository.create = AsyncMock(
            side_effect=lambda peer: _prepare_created_peer(
                peer,
                2,
            )
        )

        service.commit = AsyncMock()
        service.refresh = AsyncMock()

        data = PeerCreate(
            user_id=1,
            name="explicit-ip-peer",
            address="10.0.0.20/32",
            expires_at=None,
        )

        with patch.object(
            service.key_generator,
            "generate_keypair",
            return_value=(
                "PRIVATE_KEY_TEST",
                "PUBLIC_KEY_TEST",
            ),
        ) as mock_keypair:

            with patch.object(
                service.ip_manager,
                "get_next_ip",
                new=AsyncMock(
                    return_value="10.0.0.2/32"
                ),
            ) as mock_ip:

                result = await service.create(data)

        assert result.id == 2
        assert result.address == "10.0.0.20/32"
        assert result.public_key == "PUBLIC_KEY_TEST"
        assert result.is_active is True
        assert result.created_at is not None
        assert result.updated_at is not None

        mock_keypair.assert_called_once()
        mock_ip.assert_not_awaited()

    asyncio.run(run_test())


def test_peer_service_create_rejects_duplicate_name():
    async def run_test():
        session = MagicMock()

        service = PeerService(session)

        existing_peer = MagicMock()

        service.repository.get_by_name = AsyncMock(
            return_value=existing_peer
        )

        service.repository.create = AsyncMock()

        data = PeerCreate(
            user_id=1,
            name="duplicate-peer",
            address=None,
            expires_at=None,
        )

        with pytest.raises(
            ValueError,
            match="Peer name already exists",
        ):
            await service.create(data)

        service.repository.create.assert_not_awaited()

    asyncio.run(run_test())


def test_peer_service_create_generates_unique_keypair():
    async def run_test():
        session = MagicMock()

        service = PeerService(session)

        service.repository.get_by_name = AsyncMock(
            return_value=None
        )

        peer_counter = 0

        def create_peer(peer):
            nonlocal peer_counter

            peer_counter += 1

            return _prepare_created_peer(
                peer,
                peer_counter,
            )

        service.repository.create = AsyncMock(
            side_effect=create_peer
        )

        service.commit = AsyncMock()
        service.refresh = AsyncMock()

        data_1 = PeerCreate(
            user_id=1,
            name="unique-key-peer-1",
            address=None,
            expires_at=None,
        )

        data_2 = PeerCreate(
            user_id=1,
            name="unique-key-peer-2",
            address=None,
            expires_at=None,
        )

        service.key_generator.generate_keypair = MagicMock(
            side_effect=[
                (
                    "PRIVATE_KEY_1",
                    "PUBLIC_KEY_1",
                ),
                (
                    "PRIVATE_KEY_2",
                    "PUBLIC_KEY_2",
                ),
            ]
        )

        service.ip_manager.get_next_ip = AsyncMock(
            side_effect=[
                "10.0.0.2/32",
                "10.0.0.3/32",
            ]
        )

        result_1 = await service.create(data_1)
        result_2 = await service.create(data_2)

        assert result_1.id == 1
        assert result_2.id == 2

        assert result_1.public_key == "PUBLIC_KEY_1"
        assert result_2.public_key == "PUBLIC_KEY_2"

        assert result_1.public_key != result_2.public_key

        assert result_1.address == "10.0.0.2/32"
        assert result_2.address == "10.0.0.3/32"

        assert result_1.is_active is True
        assert result_2.is_active is True

        assert result_1.created_at is not None
        assert result_2.created_at is not None

        assert result_1.updated_at is not None
        assert result_2.updated_at is not None

    asyncio.run(run_test())