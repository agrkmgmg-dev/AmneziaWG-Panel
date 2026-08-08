from unittest.mock import patch
import subprocess

import pytest

from backend.app.services.key_generator import KeyGeneratorService


def test_generate_private_key():
    mock_result = subprocess.CompletedProcess(
        args=["wg", "genkey"],
        returncode=0,
        stdout="PRIVATE_KEY\n",
        stderr="",
    )

    with patch(
        "backend.app.services.key_generator.subprocess.run",
        return_value=mock_result,
    ) as mock_run:
        result = KeyGeneratorService.generate_private_key()

    assert result == "PRIVATE_KEY"

    mock_run.assert_called_once_with(
        ["wg", "genkey"],
        capture_output=True,
        text=True,
        check=True,
    )


def test_generate_public_key():
    mock_result = subprocess.CompletedProcess(
        args=["wg", "pubkey"],
        returncode=0,
        stdout="PUBLIC_KEY\n",
        stderr="",
    )

    with patch(
        "backend.app.services.key_generator.subprocess.run",
        return_value=mock_result,
    ) as mock_run:
        result = KeyGeneratorService.generate_public_key(
            "PRIVATE_KEY"
        )

    assert result == "PUBLIC_KEY"

    mock_run.assert_called_once_with(
        ["wg", "pubkey"],
        input="PRIVATE_KEY",
        capture_output=True,
        text=True,
        check=True,
    )


def test_generate_keypair():
    private_result = subprocess.CompletedProcess(
        args=["wg", "genkey"],
        returncode=0,
        stdout="PRIVATE_KEY\n",
        stderr="",
    )

    public_result = subprocess.CompletedProcess(
        args=["wg", "pubkey"],
        returncode=0,
        stdout="PUBLIC_KEY\n",
        stderr="",
    )

    with patch(
        "backend.app.services.key_generator.subprocess.run",
        side_effect=[
            private_result,
            public_result,
        ],
    ) as mock_run:
        service = KeyGeneratorService()

        private_key, public_key = service.generate_keypair()

    assert private_key == "PRIVATE_KEY"
    assert public_key == "PUBLIC_KEY"

    assert mock_run.call_count == 2


def test_generate_private_key_failure():
    error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["wg", "genkey"],
    )

    with patch(
        "backend.app.services.key_generator.subprocess.run",
        side_effect=error,
    ):
        with pytest.raises(
            RuntimeError,
            match="Failed to generate WireGuard private key",
        ):
            KeyGeneratorService.generate_private_key()


def test_generate_public_key_failure():
    error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["wg", "pubkey"],
    )

    with patch(
        "backend.app.services.key_generator.subprocess.run",
        side_effect=error,
    ):
        with pytest.raises(
            RuntimeError,
            match="Failed to generate WireGuard public key",
        ):
            KeyGeneratorService.generate_public_key(
                "PRIVATE_KEY"
            )