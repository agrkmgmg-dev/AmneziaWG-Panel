#!/usr/bin/env python3

import ipaddress
import os
import re
import socket
import subprocess


# The same audited helper is used twice: once for AmneziaWG and once for
# standard WireGuard.  Each instance has its own Unix socket and interface.
SOCKET_PATH = os.getenv("PANEL_SOCKET_PATH", "/run/amneziawg-panel/awg.sock")
CONTAINER = os.getenv("PANEL_CONTAINER", "amnezia-awg2")
INTERFACE = os.getenv("PANEL_INTERFACE", "awg0")
VPN_NETWORK = ipaddress.ip_network(os.getenv("PANEL_VPN_NETWORK", "10.8.1.0/24"))
VPN_COMMAND = os.getenv("PANEL_VPN_COMMAND", "awg")
ROOT_CLASS_ID = "1:1"
ROOT_QDISC = "1:"
ROOT_QDISC_HANDLE = "1:"
ROOT_QDISC_DEFAULT = "1"
ROOT_RATE = "1000mbit"

PUBLIC_KEY_RE = re.compile(
    r"^[A-Za-z0-9+/]{43}=$"
)
RATE_RE = re.compile(r"^([1-9][0-9]{0,3})mbit$")


def cleanup() -> None:
    try:
        os.unlink(SOCKET_PATH)
    except FileNotFoundError:
        pass


def run_vpn(*args: str, stdin: str | None = None) -> tuple[int, str, str]:
    result = subprocess.run(
        [
            "docker",
            "exec",
            *( ["-i"] if stdin is not None else [] ),
            CONTAINER,
            VPN_COMMAND,
            "set",
            INTERFACE,
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
        input=stdin,
    )

    return (
        result.returncode,
        result.stdout.strip(),
        result.stderr.strip(),
    )


def run_tc(*args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [
            "docker",
            "exec",
            CONTAINER,
            "tc",
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    return (
        result.returncode,
        result.stdout.strip(),
        result.stderr.strip(),
    )


def require_tc(*args: str) -> None:
    code, stdout, stderr = run_tc(*args)
    if code != 0:
        raise RuntimeError(
            stderr
            or stdout
            or "tc command failed"
        )


def validate_public_key(value: str) -> None:
    if not PUBLIC_KEY_RE.fullmatch(value):
        raise ValueError("invalid public key")


def validate_allowed_ips(value: str) -> None:
    if not value or not value.strip():
        raise ValueError("invalid allowed-ips")

    for item in value.split(","):
        item = item.strip()

        if not item:
            raise ValueError("invalid allowed-ips")

        try:
            ipaddress.ip_network(item, strict=False)
        except ValueError as exc:
            raise ValueError("invalid allowed-ips") from exc


def validate_rate(address: str, rate: str) -> tuple[ipaddress.IPv4Address, int]:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError as exc:
        raise ValueError("invalid peer address") from exc

    if not isinstance(ip, ipaddress.IPv4Address) or ip not in VPN_NETWORK:
        raise ValueError("peer address is outside the VPN network")

    match = RATE_RE.fullmatch(rate)
    if match is None:
        raise ValueError("invalid rate")

    mbps = int(match.group(1))
    if not 1 <= mbps <= 10000:
        raise ValueError("rate is outside the supported range")

    return ip, mbps


def peer_class_id(ip: ipaddress.IPv4Address) -> str:
    """Return a stable, separate HTB class for each address in the /24 pool."""
    return f"1:{1000 + int(ip.packed[-1])}"


def ensure_rate_qdisc() -> None:
    code, stdout, stderr = run_tc(
        "qdisc",
        "show",
        "dev",
        INTERFACE,
    )
    if code != 0:
        raise RuntimeError(
            stderr
            or stdout
            or "could not inspect traffic control"
        )

    if f"qdisc htb {ROOT_QDISC}" not in stdout:
        require_tc(
            "qdisc",
            "replace",
            "dev",
            INTERFACE,
            "root",
            "handle",
            ROOT_QDISC_HANDLE,
            "htb",
            "default",
            ROOT_QDISC_DEFAULT,
        )

    require_tc(
        "class",
        "replace",
        "dev",
        INTERFACE,
        "parent",
        ROOT_QDISC,
        "classid",
        ROOT_CLASS_ID,
        "htb",
        "rate",
        ROOT_RATE,
        "ceil",
        ROOT_RATE,
    )
    require_tc(
        "qdisc",
        "replace",
        "dev",
        INTERFACE,
        "parent",
        ROOT_CLASS_ID,
        "handle",
        "10:",
        "fq_codel",
    )


def set_peer_rate_limit(address: str, rate: str) -> None:
    ip, mbps = validate_rate(address, rate)
    class_id = peer_class_id(ip)
    priority = class_id.split(":", 1)[1]

    # Download packets leave awg0 with the VPN client's address as destination.
    # A distinct HTB class guarantees that one peer cannot consume another
    # peer's share of the available outbound bandwidth.
    ensure_rate_qdisc()
    require_tc(
        "class",
        "replace",
        "dev",
        INTERFACE,
        "parent",
        ROOT_QDISC,
        "classid",
        class_id,
        "htb",
        "rate",
        f"{mbps}mbit",
        "ceil",
        f"{mbps}mbit",
    )
    require_tc(
        "qdisc",
        "replace",
        "dev",
        INTERFACE,
        "parent",
        class_id,
        "handle",
        f"{priority}:",
        "fq_codel",
    )
    require_tc(
        "filter",
        "replace",
        "dev",
        INTERFACE,
        "protocol",
        "ip",
        "parent",
        ROOT_QDISC,
        "prio",
        priority,
        "u32",
        "match",
        "ip",
        "dst",
        f"{ip}/32",
        "flowid",
        class_id,
    )


def handle_request(conn: socket.socket) -> None:
    raw = conn.recv(4096).decode(
        "utf-8",
        errors="replace",
    ).strip()

    if not raw:
        conn.sendall(b"ERROR empty request\n")
        return

    parts = raw.split()

    try:
        command = parts[0]

        # ---------------------------------------------
        # READ
        # ---------------------------------------------

        if command == "dump" and len(parts) == 1:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    CONTAINER,
                VPN_COMMAND,
                    "show",
                    INTERFACE,
                    "dump",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )

            if result.returncode != 0:
                error = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "VPN show failed"
                )

                conn.sendall(
                    f"ERROR {error}\n".encode()
                )
                return

            conn.sendall(
                result.stdout.encode(
                    "utf-8",
                    errors="replace",
                )
            )
            return

        # ---------------------------------------------
        # ADD
        # ---------------------------------------------

        if command == "add":
            if len(parts) not in (3, 4):
                raise ValueError(
                    "usage: add PUBLIC_KEY ALLOWED_IPS [PRESHARED_KEY]"
                )

            public_key = parts[1]
            allowed_ips = parts[2]
            preshared_key = parts[3] if len(parts) == 4 else None
            if len(parts) not in (3, 4):
                raise ValueError("usage: add PUBLIC_KEY ALLOWED_IPS [PRESHARED_KEY]")

            validate_public_key(public_key)
            if preshared_key:
                validate_public_key(preshared_key)
            validate_allowed_ips(allowed_ips)

            if preshared_key:
                command = "cat > /tmp/panel-peer-psk && \"$0\" set \"$1\" peer \"$2\" allowed-ips \"$3\" preshared-key /tmp/panel-peer-psk; status=$?; rm -f /tmp/panel-peer-psk; exit $status"
                result = subprocess.run(["docker", "exec", "-i", CONTAINER, "sh", "-c", command, VPN_COMMAND, INTERFACE, public_key, allowed_ips], input=preshared_key + "\n", capture_output=True, text=True, check=False, timeout=15)
                code, stdout, stderr = result.returncode, result.stdout.strip(), result.stderr.strip()
            else:
                code, stdout, stderr = run_vpn("peer", public_key, "allowed-ips", allowed_ips)

            if code != 0:
                raise RuntimeError(
                    stderr
                    or stdout
                    or "VPN add failed"
                )

            conn.sendall(b"OK\n")
            return

        # ---------------------------------------------
        # REMOVE
        # ---------------------------------------------

        if command == "remove":
            if len(parts) != 2:
                raise ValueError(
                    "usage: remove PUBLIC_KEY"
                )

            public_key = parts[1]

            validate_public_key(public_key)

            code, stdout, stderr = run_vpn(
                "peer",
                public_key,
                "remove",
            )

            if code != 0:
                raise RuntimeError(
                    stderr
                    or stdout
                    or "VPN remove failed"
                )

            conn.sendall(b"OK\n")
            return

        # ---------------------------------------------
        # UPDATE ALLOWED IPS
        # ---------------------------------------------

        if command == "allowed-ips":
            if len(parts) != 3:
                raise ValueError(
                    "usage: allowed-ips PUBLIC_KEY ALLOWED_IPS"
                )

            public_key = parts[1]
            allowed_ips = parts[2]
            preshared_key = parts[3] if len(parts) == 4 else None
            if len(parts) not in (3, 4):
                raise ValueError("usage: add PUBLIC_KEY ALLOWED_IPS [PRESHARED_KEY]")

            validate_public_key(public_key)
            if preshared_key:
                validate_public_key(preshared_key)
            validate_allowed_ips(allowed_ips)

            code, stdout, stderr = run_vpn(
                "peer",
                public_key,
                "allowed-ips",
                allowed_ips,
            )

            if code != 0:
                raise RuntimeError(
                    stderr
                    or stdout
                    or "VPN allowed-ips failed"
                )

            conn.sendall(b"OK\n")
            return

        # ---------------------------------------------
        # DOWNLOAD RATE LIMIT
        # ---------------------------------------------

        if command == "rate":
            if len(parts) != 3:
                raise ValueError(
                    "usage: rate PEER_ADDRESS RATE"
                )

            set_peer_rate_limit(parts[1], parts[2])
            conn.sendall(b"OK\n")
            return

        raise ValueError(
            f"unknown command: {command}"
        )

    except Exception as exc:
        conn.sendall(
            f"ERROR {exc}\n".encode(
                "utf-8",
                errors="replace",
            )
        )


def main() -> None:
    cleanup()

    os.makedirs(
        os.path.dirname(SOCKET_PATH),
        mode=0o755,
        exist_ok=True,
    )

    server = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )

    try:
        server.bind(SOCKET_PATH)

        os.chmod(
            SOCKET_PATH,
            0o660,
        )

        server.listen(16)

        while True:
            conn, _ = server.accept()

            try:
                handle_request(conn)
            finally:
                conn.close()

    finally:
        server.close()
        cleanup()


if __name__ == "__main__":
    main()
