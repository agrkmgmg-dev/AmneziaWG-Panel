"""
Official WireGuard Key Generator Service.
"""

from __future__ import annotations

import subprocess


class KeyGeneratorService:
    """
    Generate WireGuard key pairs using the official wg tool.
    """

    @staticmethod
    def generate_private_key() -> str:
        """
        Generate a private key using `wg genkey`.
        """
        try:
            result = subprocess.run(
                ["wg", "genkey"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Failed to generate WireGuard private key."
            ) from exc

        return result.stdout.strip()

    @staticmethod
    def generate_public_key(
        private_key: str,
    ) -> str:
        """
        Generate a public key from a private key.
        """
        try:
            result = subprocess.run(
                ["wg", "pubkey"],
                input=private_key,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Failed to generate WireGuard public key."
            ) from exc

        return result.stdout.strip()

    def generate_keypair(
        self,
    ) -> tuple[str, str]:
        """
        Generate WireGuard private/public key pair.
        """
        private_key = self.generate_private_key()
        public_key = self.generate_public_key(private_key)

        return private_key, public_key