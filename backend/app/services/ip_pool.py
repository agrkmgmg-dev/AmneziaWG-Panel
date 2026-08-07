"""
IP Pool Manager Service.
"""

from ipaddress import IPv4Network, IPv4Address


class IPPoolService:
    """
    Manage available client IP addresses.
    """

    def __init__(
        self,
        subnet: str = "10.0.0.0/24",
        server_ip: str = "10.0.0.1",
    ) -> None:

        self.network = IPv4Network(subnet)
        self.server_ip = IPv4Address(server_ip)


    def get_available_ips(
        self,
        used_ips: list[str],
    ) -> list[str]:
        """
        Return available client IPs.
        """

        used = {
            IPv4Address(
                ip.replace("/32", "")
            )
            for ip in used_ips
        }

        available = []

        for ip in self.network.hosts():

            if ip == self.server_ip:
                continue

            if ip in used:
                continue

            available.append(
                f"{ip}/32"
            )

        return available


    def get_next_ip(
        self,
        used_ips: list[str],
    ) -> str:
        """
        Return next free IP.
        """

        available = self.get_available_ips(
            used_ips
        )

        if not available:
            raise RuntimeError(
                "IP pool exhausted"
            )

        return available[0]


    def get_statistics(
        self,
        used_ips: list[str],
    ) -> dict:
        """
        Return IP pool statistics.
        """

        total = self.network.num_addresses - 2

        used = len(used_ips)

        available = total - used

        return {
            "subnet": str(self.network),
            "total": total,
            "used": used,
            "available": available,
        }