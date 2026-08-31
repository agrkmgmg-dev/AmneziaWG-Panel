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

    def set_rate_limit(self, address: str, mbps: int = 15) -> None:
        from backend.app.services.rate_limit import peer_rate_request

        request = peer_rate_request(address, mbps)
        self._request(request)

    def _request(self, request: str) -> str:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.settimeout(10)
            sock.connect(self.socket_path)
            sock.sendall(request.encode())
            sock.shutdown(socket.SHUT_WR)
            return sock.recv(4096).decode(errors="replace").strip()
        finally:
            sock.close()
