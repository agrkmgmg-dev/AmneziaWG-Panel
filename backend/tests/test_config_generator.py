from pathlib import Path

from backend.app.models.peer import Peer
from backend.app.services.config_generator import ConfigGeneratorService


def create_test_peer() -> Peer:
    return Peer(
        id=1,
        user_id=1,
        name="test-peer",
        public_key="CLIENT_PUBLIC_KEY",
        private_key="CLIENT_PRIVATE_KEY",
        address="10.10.0.2/32",
        is_active=True,
    )


def test_generate_config():
    service = ConfigGeneratorService(
        endpoint="vpn.example.com:51820",
        server_public_key="SERVER_PUBLIC_KEY",
    )

    peer = create_test_peer()

    config = service.generate(peer)

    assert "[Interface]" in config
    assert "PrivateKey = CLIENT_PRIVATE_KEY" in config
    assert "Address = 10.10.0.2/32" in config

    assert "[Peer]" in config
    assert "PublicKey = SERVER_PUBLIC_KEY" in config
    assert "Endpoint = vpn.example.com:51820" in config
    assert "AllowedIPs = 0.0.0.0/0, ::/0" in config
    assert "PersistentKeepalive = 25" in config


def test_generate_qr():
    service = ConfigGeneratorService(
        endpoint="vpn.example.com:51820",
        server_public_key="SERVER_PUBLIC_KEY",
    )

    peer = create_test_peer()

    qr_path = service.generate_qr(peer)

    assert qr_path.endswith("peer_1.png")
    assert Path(qr_path).exists()

    # Cleanup test artifact
    Path(qr_path).unlink()