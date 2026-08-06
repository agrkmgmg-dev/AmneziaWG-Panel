"""
Admin dashboard router.

Provides web admin pages.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.services.dashboard import DashboardService


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


templates = Jinja2Templates(
    directory="backend/app/templates",
)


async def get_dashboard_service(
    session: AsyncSession = Depends(get_db),
) -> DashboardService:
    """
    Provide DashboardService instance.
    """

    return DashboardService(session)


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
) -> HTMLResponse:
    """
    Render admin dashboard page.
    """

    stats = await service.get_dashboard_stats()

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "request": request,
            **stats,
        },
    )