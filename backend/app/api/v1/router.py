from fastapi import APIRouter

from backend.app.api.v1.activity_logs import (
    router as activity_logs_router,
)

from backend.app.api.v1.users import (
    router as users_router,
)

from backend.app.api.v1.peers import (
    router as peers_router,
)

from backend.app.api.v1.traffic import (
    router as traffic_router,
)

from backend.app.api.v1.auth import (
    router as auth_router,
)
from backend.app.api.v1.devices import (
    router as devices_router,
)


api_router = APIRouter(
    prefix="/api/v1",
    tags=["API v1"],
)

_routers_registered = False


def register_routers() -> None:
    """
    Register API v1 routers.
    """

    global _routers_registered
    if _routers_registered:
        return

    api_router.include_router(
        auth_router,
    )

    api_router.include_router(
        devices_router,
    )

    api_router.include_router(
        users_router,
    )

    api_router.include_router(
        peers_router,
    )

    api_router.include_router(
        traffic_router,
    )

    api_router.include_router(
        activity_logs_router,
    )

    _routers_registered = True
