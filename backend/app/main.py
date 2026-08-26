"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.app.admin import router as admin_router

from backend.app.api.v1.router import (
    api_router,
    register_routers,
)

from backend.app.core.config import settings
from backend.app.scheduler.traffic_scheduler import TrafficScheduler


traffic_scheduler = TrafficScheduler(
    interval=60
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    """

    # Start background services
    await traffic_scheduler.start()

    print(
        "Traffic Scheduler started"
    )

    yield

    # Stop background services
    await traffic_scheduler.stop()

    print(
        "Traffic Scheduler stopped"
    )


def create_application() -> FastAPI:
    """
    Application factory.
    """

    app = FastAPI(
        title="AmneziaWG Panel",
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    @app.get("/", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Return a lightweight liveness response for load balancers."""

        return {
            "status": "ok",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        """Alias for deployments that conventionally probe ``/health``."""

        return {"status": "ok"}

    # Session middleware for admin authentication
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
    )


    # Static files
    app.mount(
        "/static",
        StaticFiles(
            directory=str(
                Path(__file__).resolve().parent / "static"
            ),
        ),
        name="static",
    )


    # Register API v1 routes
    register_routers()


    # API routes
    app.include_router(
        api_router
    )


    # Admin routes
    app.include_router(
        admin_router
    )


    return app


app = create_application()
