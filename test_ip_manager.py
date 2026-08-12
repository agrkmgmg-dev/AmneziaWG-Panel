import asyncio

from backend.app.services.ip_manager import IPManagerService


class FakePeer:
    def __init__(self, address: str):
        self.address = address


class FakePeerRepository:
    def __init__(self, peers: list[FakePeer]):
        self.peers = peers

    async def get_all(self):
        return self.peers


def test_get_next_ip_returns_first_available_ip():
    repository = FakePeerRepository([])

    service = IPManagerService(repository)

    ip = asyncio.run(service.get_next_ip())

    assert ip == "10.0.0.2/32"


def test_get_next_ip_skips_used_ips():
    repository = FakePeerRepository(
        [
            FakePeer("10.0.0.2/32"),
            FakePeer("10.0.0.3/32"),
        ]
    )

    service = IPManagerService(repository)

    ip = asyncio.run(service.get_next_ip())

    assert ip == "10.0.0.4/32"


def test_get_next_ip_ignores_empty_addresses():
    repository = FakePeerRepository(
        [
            FakePeer(""),
            FakePeer("10.0.0.2/32"),
            FakePeer("10.0.0.3/32"),
        ]
    )

    service = IPManagerService(repository)

    ip = asyncio.run(service.get_next_ip())

    assert ip == "10.0.0.4/32"


def test_get_next_ip_skips_server_ip():
    repository = FakePeerRepository(
        [
            FakePeer("10.0.0.1/32"),
        ]
    )

    service = IPManagerService(repository)

    ip = asyncio.run(service.get_next_ip())

    assert ip == "10.0.0.2/32"


def test_get_next_ip_returns_next_available_ip():
    repository = FakePeerRepository(
        [
            FakePeer("10.0.0.2/32"),
            FakePeer("10.0.0.3/32"),
            FakePeer("10.0.0.4/32"),
            FakePeer("10.0.0.5/32"),
        ]
    )

    service = IPManagerService(repository)

    ip = asyncio.run(service.get_next_ip())

    assert ip == "10.0.0.6/32"