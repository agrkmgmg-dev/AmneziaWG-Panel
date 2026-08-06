from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.admin import router as admin_router
from backend.app.api.v1 import api_router


def create_application() -> FastAPI:
    """
    Application factory.
    """

    app = FastAPI(
        title="AmneziaWG Panel",
        version="0.4.0",
    )

    app.mount(
        "/static",
        StaticFiles(directory="backend/app/static"),
        name="static",
    )

    app.include_router(api_router)
    app.include_router(admin_router)

    return app


app = create_application()