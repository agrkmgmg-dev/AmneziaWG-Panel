"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.app.admin import router as admin_router
from backend.app.api.v1 import api_router
from backend.app.core.config import settings


def create_application() -> FastAPI:
    """
    Application factory.
    """

    app = FastAPI(
        title="AmneziaWG Panel",
        version="0.4.0",
    )

    # Session middleware for admin authentication
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
    )

    # Static files
    app.mount(
        "/static",
        StaticFiles(
            directory="backend/app/static",
        ),
        name="static",
    )

    # API routes
    app.include_router(api_router)

    # Admin routes
    app.include_router(admin_router)

    return app


app = create_application()