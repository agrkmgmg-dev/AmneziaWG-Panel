"""
Security utilities.

Provides password hashing and verification helpers.
"""

from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.

    Args:
        password: Plain-text password.

    Returns:
        Secure password hash.
    """
    return _password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against a stored hash.

    Args:
        plain_password: Password provided by the user.
        hashed_password: Stored password hash.

    Returns:
        True if password matches, otherwise False.
    """
    return _password_hash.verify(
        plain_password,
        hashed_password,
    )