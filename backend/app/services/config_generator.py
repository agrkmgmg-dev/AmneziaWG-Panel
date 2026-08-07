"""
AmneziaWG Config Generator Service.
"""

from backend.app.models.peer import Peer


class ConfigGeneratorService:
    """
    Generate AmneziaWG client configuration.
    """

    def __init__(
        self,
        endpoint: str,
        server_public_key: str,
    ) -> None:

        self.endpoint = endpoint
        self.server_public_key = server_public_key


    def generate(
        self,
        peer: Peer,
    ) -> str:
        """
        Generate client.conf content.
        """

        config = f"""
[Interface]
PrivateKey = {peer.private_key}
Address = {peer.address}

[Peer]
PublicKey = {self.server_public_key}
Endpoint = {self.endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""

        return config.strip()