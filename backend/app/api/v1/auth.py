"""
Authentication API router.

Handles:
- Login
- Token refresh
- Current user
- Logout
"""

from fastapi import APIRouter


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/health")
async def auth_health() -> dict:
    """
    Auth module health check.
    """

    return {
        "module": "auth",
        "status": "ok",
    }