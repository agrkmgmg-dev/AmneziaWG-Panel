"""Bandwidth limit policy for AmneziaWG peers."""

from ipaddress import ip_interface


DEFAULT_RATE_MBPS = 15


def validate_rate(mbps: int) -> int:
    if not 1 <= mbps <= 10000:
        raise ValueError("سرعت باید بین 1 تا 10000 مگابیت باشد")
    return mbps


def peer_rate_request(address: str, mbps: int = DEFAULT_RATE_MBPS) -> str:
    """Build the restricted request consumed by the privileged host helper."""
    validate_rate(mbps)
    ip = ip_interface(address).ip
    return f"rate {ip} {mbps}mbit"
