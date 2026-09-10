"""Generate client configuration files for AmneziaWG and WireGuard."""

from pathlib import Path

from backend.app.core.config import BASE_DIR, settings
from backend.app.models.peer import Peer
from backend.app.utils.qr import generate_qr


class ConfigGeneratorService:
    """
    Generate VPN client configuration and QR code.
    """

    def __init__(
        self,
        endpoint: str | None = None,
        server_public_key: str | None = None,
    ) -> None:
        self.endpoint = endpoint or settings.AWG_ENDPOINT
        self.server_public_key = (
            server_public_key or settings.AWG_SERVER_PUBLIC_KEY
        )

        # Resolve from the package location rather than the process cwd so
        # QR generation works under systemd, Docker, and ``uvicorn`` started
        # from any directory.
        self.qr_path = BASE_DIR / "app" / "static" / "qr"

        self.qr_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate(
        self,
        peer: Peer,
    ) -> str:
        """
        Generate a config matching the peer's selected protocol.
        """

        if peer.protocol == "wireguard":
            return self._generate_wireguard(peer)

        return self._generate_amneziawg(peer)

    def _generate_wireguard(self, peer: Peer) -> str:
        """Generate a standard, interoperable WireGuard configuration."""
        config = f"""[Interface]
PrivateKey = {peer.private_key}
Address = {peer.address}
DNS = 1.1.1.1, 1.0.0.1

[Peer]
PublicKey = {settings.WG_SERVER_PUBLIC_KEY}
{f"PresharedKey = {peer.preshared_key}" if peer.preshared_key else ""}
Endpoint = {settings.WG_ENDPOINT}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""
        return config.strip()

    def _generate_amneziawg(self, peer: Peer) -> str:
        """Generate an AmneziaWG client configuration."""

        config = f"""[Interface]
PrivateKey = {peer.private_key}
Address = {peer.address}
DNS = 172.29.172.254, 1.0.0.1
Jc = {settings.AWG_JC}
Jmin = {settings.AWG_JMIN}
Jmax = {settings.AWG_JMAX}
S1 = {settings.AWG_S1}
S2 = {settings.AWG_S2}
S3 = {settings.AWG_S3}
S4 = {settings.AWG_S4}
H1 = {settings.AWG_H1}
H2 = {settings.AWG_H2}
H3 = {settings.AWG_H3}
H4 = {settings.AWG_H4}
{f"I1 = {peer.amnezia_i1 or settings.AWG_I1}" if (peer.amnezia_i1 or settings.AWG_I1) else ""}

[Peer]
PublicKey = {self.server_public_key}
{f"PresharedKey = {peer.preshared_key}" if peer.preshared_key else ""}
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
