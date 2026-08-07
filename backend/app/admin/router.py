"""
Admin dashboard and authentication router.
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.auth import (
    is_admin_authenticated,
    login_admin,
    logout_admin,
)
from backend.app.db.database import get_db
from backend.app.services.admin_user import AdminUserService
from backend.app.services.dashboard import DashboardService


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

templates = Jinja2Templates(
    directory="backend/app/templates",
)


# =====================================================
# Dependencies
# =====================================================

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


# =====================================================
# Login Page
# =====================================================

@router.get(
    "/login",
    response_class=HTMLResponse,
)
async def login_page(
    request: Request,
) -> HTMLResponse:
    """
    Render admin login page.
    """

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "request": request,
            "error": None,
        },
    )


# =====================================================
# Login Handler
# =====================================================

@router.post(
    "/login",
)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
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


# =====================================================
# Dashboard
# =====================================================

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


# =====================================================
# Users
# =====================================================

@router.get(
    "/users",
    response_class=HTMLResponse,
)
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

# =====================================================
# Logout
# =====================================================

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
# =====================================================
# Delete User
# =====================================================

@router.get(
    "/users/{user_id}/delete",
)
async def delete_user(
    user_id: int,
    request: Request,
    service: AdminUserService = Depends(get_admin_user_service),
):
    """
    Delete user.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    await service.delete_user(
        user_id
    )

    return RedirectResponse(
        url="/admin/users",
        status_code=302,
    )

# =====================================================
# Create User - Form
# =====================================================

@router.get(
    "/users/create",
    response_class=HTMLResponse,
)
async def create_user_page(
    request: Request,
) -> HTMLResponse:
    """
    Render create user form.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/create_user.html",
        context={
            "request": request,
            "error": None,
        },
    )
# =====================================================
# Create User - Submit
# =====================================================

@router.post(
    "/users/create",
    response_class=HTMLResponse,
)
async def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    service: AdminUserService = Depends(get_admin_user_service),
) -> HTMLResponse:
    """
    Create new user.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    user = await service.create_user(
        username=username,
        password=password,
    )

    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="admin/create_user.html",
            context={
                "request": request,
                "error": "این نام کاربری قبلا ثبت شده است",
            },
        )

    return RedirectResponse(
        url="/admin/users",
        status_code=302,
    )