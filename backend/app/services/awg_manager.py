"""Small client for the host-side AWG control socket."""

import socket


class AWGManagerService:
    def __init__(self, socket_path: str = "/run/amneziawg-panel/awg.sock"):
        self.socket_path = socket_path

    def remove_peer(self, public_key: str) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.settimeout(10)
            sock.connect(self.socket_path)
            sock.sendall(f"remove {public_key}".encode())
            sock.shutdown(socket.SHUT_WR)
            response = sock.recv(4096).decode(errors="replace").strip()
        finally:
            sock.close()
        if response.startswith("ERROR"):
            raise RuntimeError(response)
