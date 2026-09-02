"""Import existing WireGuard/AmneziaWG client configurations."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ImportedConfig:
    private_key: str
    address: str
    server_public_key: str
    endpoint: str | None
    preshared_key: str | None


def parse_config(text: str) -> ImportedConfig:
    section = ""
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().lower()
            continue
        if "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        values[f"{section}.{key.lower()}"] = value

    private_key = values.get("interface.privatekey")
    address = values.get("interface.address")
    server_key = values.get("peer.publickey")
    endpoint = values.get("peer.endpoint")
    preshared_key = values.get("peer.presharedkey")
    if not private_key or not address or not server_key:
        raise ValueError("کانفیگ باید PrivateKey، Address و PublicKey داشته باشد")
    return ImportedConfig(private_key, address, server_key, endpoint, preshared_key)
