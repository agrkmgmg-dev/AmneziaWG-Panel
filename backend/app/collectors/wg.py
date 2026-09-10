"""Standard WireGuard traffic collector via the host control socket."""

from backend.app.collectors.awg import AWGCollector


class WGCollector(AWGCollector):
    """Collect counters from the dedicated standard WireGuard interface."""

    def __init__(self, interface: str = "wg0") -> None:
        super().__init__(interface=interface)
        self.socket_path = "/run/amneziawg-panel/wg.sock"
        # The production panel communicates through the helper.  Keeping the
        # AWG fallback behavior makes tests and local development work too.
        from pathlib import Path
        from shutil import which
        self.mock_mode = which("wg") is None and not Path(self.socket_path).exists()
