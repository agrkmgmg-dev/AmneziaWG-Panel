"""
AmneziaWG Config Generator Service.
"""

from pathlib import Path

from backend.app.models.peer import Peer
from backend.app.utils.qr import generate_qr


class ConfigGeneratorService:
    """
    Generate AmneziaWG client configuration and QR code.
    """

    def __init__(
        self,
        endpoint: str,
        server_public_key: str,
    ) -> None:
        self.endpoint = endpoint
        self.server_public_key = server_public_key

        self.qr_path = Path(
            "backend/app/static/qr"
        )

        self.qr_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate(
        self,
        peer: Peer,
    ) -> str:
        """
        Generate AmneziaWG client config.
        """

        config = f"""[Interface]
PrivateKey = {peer.private_key}
Address = {peer.address}

[Peer]
PublicKey = {self.server_public_key}
Endpoint = {self.endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""

        return config.strip()

    def generate_qr(
        self,
        peer: Peer,
    ) -> str:
        """
        Generate QR code PNG from config.
        """

        config = self.generate(peer)

        filename = f"peer_{peer.id}.png"

        path = self.qr_path / filename

        generate_qr(
            data=config,
            path=str(path),
        )

        return str(path)