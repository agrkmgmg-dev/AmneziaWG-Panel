"""
AmneziaWG Traffic Collector.

Supports real AWG mode and development mock mode.
"""

import subprocess
from shutil import which


class AWGCollector:
    """
    Collect traffic from AmneziaWG.
    """

    def __init__(
        self,
        interface: str = "awg0",
    ) -> None:

        self.interface = interface
        self.mock_mode = which("awg") is None


    def get_dump(self) -> str:
        """
        Get AWG dump output.
        """

        if self.mock_mode:
            return self.mock_dump()


        result = subprocess.run(
            [
                "awg",
                "show",
                self.interface,
                "dump",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        return result.stdout


    def mock_dump(self) -> str:
        """
        Development fake dump.
        """

        return """
privatekey publickey 10.0.0.2/32 1000000 500000 1700000000
privatekey publickey 10.0.0.3/32 2500000 1500000 1700000000
"""


    def collect(self) -> list[dict]:
        """
        Parse dump data.
        """

        dump = self.get_dump()

        peers = []

        for line in dump.strip().splitlines():

            parts = line.split()

            if len(parts) < 5:
                continue

            peers.append(
                {
                    "address": parts[2],
                    "download_bytes": int(parts[3]),
                    "upload_bytes": int(parts[4]),
                }
            )

        return peers