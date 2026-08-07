"""
Admin authentication helpers.
"""

from fastapi import Request


SESSION_KEY = "admin_authenticated"


def login_admin(
    request: Request,
) -> None:
    """
    Create admin session.
    """

    request.session[SESSION_KEY] = True


def logout_admin(
    request: Request,
) -> None:
    """
    Remove admin session.
    """

    request.session.pop(
        SESSION_KEY,
        None,
    )


def is_admin_authenticated(
    request: Request,
) -> bool:
    """
    Check admin authentication status.
    """

    return bool(
        request.session.get(
            SESSION_KEY,
            False,
        )
    )