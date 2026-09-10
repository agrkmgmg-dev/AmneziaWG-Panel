"""Small client for the host-side standard WireGuard control socket."""

from backend.app.services.awg_manager import AWGManagerService


class WGManagerService(AWGManagerService):
    """Use the same safe helper protocol on the separate WireGuard socket."""

    def __init__(self, socket_path: str = "/run/amneziawg-panel/wg.sock"):
        super().__init__(socket_path=socket_path)
