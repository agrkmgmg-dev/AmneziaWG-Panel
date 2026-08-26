"""Production entry point for the AmneziaWG Panel backend.

This module intentionally re-exports the FastAPI application so the project
can be started with the conventional command::

    uvicorn backend.main:app

Keeping the import here also makes deployments (Docker/systemd/process
managers) independent of the internal ``backend.app`` package layout.
"""

from backend.app.main import app, create_application

__all__ = ["app", "create_application"]
