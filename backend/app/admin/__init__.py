"""
Admin dashboard router.

Provides web admin pages.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from backend.app.admin.router import router


__all__ = [
    "router",
]

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
) -> HTMLResponse:
    """
    Admin dashboard page.
    """

    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>AmneziaWG Panel</title>
        </head>

        <body>
            <h1>AmneziaWG Panel</h1>
            <p>Admin Dashboard Foundation</p>
        </body>
        </html>
        """
    )