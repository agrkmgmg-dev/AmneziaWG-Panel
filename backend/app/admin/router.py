"""
Admin dashboard and authentication router.
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.admin_user import AdminUserService
from backend.app.admin.auth import (
    login_admin,
    logout_admin,
    is_admin_authenticated,
)
from backend.app.db.database import get_db
from backend.app.services.dashboard import DashboardService
from backend.app.services.admin_user import AdminUserService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)
# ---------------------------------------------------
# Users Page (Release 0.5)
# ---------------------------------------------------
async def get_admin_user_service(
    session: AsyncSession = Depends(get_db),
) -> AdminUserService:
    """
    Provide AdminUserService instance.
    """
    return AdminUserService(session)
    response_class=HTMLResponse,

async def users(
    request: Request,
    service: AdminUserService = Depends(get_admin_user_service),
) -> HTMLResponse:
    """
    Render users management page.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    users = await service.get_users()

    return templates.TemplateResponse(
        request=request,
        name="admin/users.html",
        context={
            "request": request,
            "users": users,
        },
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
async def get_admin_user_service(
    session: AsyncSession = Depends(get_db),
) -> AdminUserService:
    """
    Provide AdminUserService instance.
    """

    return AdminUserService(session)

# ---------------------------------------------------
# Login Page
# ---------------------------------------------------

# ---------------------------------------------------
# Login Handler
# ---------------------------------------------------

@router.post(
    "/login",
    response_class=HTMLResponse,
)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> HTMLResponse:
    """
    Handle admin login.
    """

    if username == "admin" and password == "123456":
        login_admin(request)

        return RedirectResponse(
            url="/admin/dashboard",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "request": request,
            "error": "نام کاربری یا رمز عبور اشتباه است",
        },
    )


# ---------------------------------------------------
# Dashboard
# ---------------------------------------------------

@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
) -> HTMLResponse:
    """
    Render admin dashboard.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    stats = await service.get_dashboard_stats()

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "request": request,
            **stats,
        },
    )


# ---------------------------------------------------
# Users Page (Release 0.5)
# ---------------------------------------------------

@router.get(
    "/users",
    response_class=HTMLResponse,
)
async def users(
    request: Request,
) -> HTMLResponse:
    """
    Render users management page.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/users.html",
        context={
            "request": request,
        },
    )


# ---------------------------------------------------
# Logout
# ---------------------------------------------------

@router.get(
    "/logout",
)
async def logout(
    request: Request,
):
    """
    Logout admin user.
    """

    logout_admin(request)

    return RedirectResponse(
        url="/admin/login",
        status_code=302,
    )