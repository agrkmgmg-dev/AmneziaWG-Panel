"""
AmneziaWG Traffic Collector.

Supports real AWG mode and development mock mode.
"""

import subprocess
import socket
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
        self.socket_path = "/run/amneziawg-panel/awg.sock"
        self.mock_mode = which("awg") is None


    def get_dump(self) -> str:
        """
        Get AWG dump output.
        """

        # In production the panel container cannot see the host network
        # namespace. Read the authoritative dump through the host helper.
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect(self.socket_path)
            sock.sendall(b"dump")
            sock.shutdown(socket.SHUT_WR)
            response = b""
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                response += chunk
            sock.close()
            text = response.decode("utf-8", errors="replace")
            if text and not text.startswith("ERROR"):
                return text
        except (OSError, socket.timeout):
            pass

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

            # `awg show <iface> dump` starts with one interface row.  Peer
            # rows have allowed-ips at index 3, while the compact mock format
            # used by tests has the address at index 2.
            if len(parts) >= 8 and "/" in parts[3]:
                address_index = 3
                rx_index = 5
                tx_index = 6
            else:
                address_index = 2
                rx_index = 4
                tx_index = 3

            address = parts[address_index]
            if "/" not in address:
                continue

            peers.append(
                {
                    "address": address,
                    "download_bytes": int(parts[tx_index]),
                    "upload_bytes": int(parts[rx_index]),
                }
            )

        return peers
