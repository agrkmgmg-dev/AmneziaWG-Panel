"""
Admin dashboard router.

Provides web admin pages.
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


templates = Jinja2Templates(
    directory="backend/app/templates",
)


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
) -> HTMLResponse:
    """
    Render admin dashboard page.
    """

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "users_count": 0,
            "peers_count": 0,
            "traffic_count": 0,
            "logs_count": 0,
        },
    )