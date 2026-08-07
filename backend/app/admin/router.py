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
from backend.app.services.admin_peer import AdminPeerService
from backend.app.services.admin_peer import AdminPeerService
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
async def get_admin_peer_service(
    session: AsyncSession = Depends(get_db),
) -> AdminPeerService:
    """
    Provide AdminPeerService instance.
    """

    return AdminPeerService(session)

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
# Peers
# =====================================================

@router.get(
    "/peers",
    response_class=HTMLResponse,
)
async def peers(
    request: Request,
    service: AdminPeerService = Depends(get_admin_peer_service),
) -> HTMLResponse:
    """
    Render peers management page.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    peers = await service.get_peers()

    return templates.TemplateResponse(
        request=request,
        name="admin/peers.html",
        context={
            "request": request,
            "peers": peers,
        },
    )
@router.get(
    "/peers/create",
    response_class=HTMLResponse,
)
async def create_peer_page(
    request: Request,
) -> HTMLResponse:
    """
    Render create peer form.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/create_peer.html",
        context={
            "request": request,
        },
    )
@router.post(
    "/peers/create",
)
async def create_peer(
    request: Request,
    user_id: int = Form(...),
    name: str = Form(...),
    public_key: str = Form(...),
    address: str = Form(...),
    private_key: str | None = Form(None),
    service: AdminPeerService = Depends(get_admin_peer_service),
):
    """
    Create new peer.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    await service.create_peer(
        user_id=user_id,
        name=name,
        public_key=public_key,
        address=address,
        private_key=private_key,
    )

    return RedirectResponse(
        url="/admin/peers",
        status_code=302,
    )
@router.get(
    "/peers/{peer_id}/delete",
)
async def delete_peer(
    peer_id: int,
    request: Request,
    service: AdminPeerService = Depends(get_admin_peer_service),
):
    """
    Delete peer.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    await service.delete_peer(
        peer_id
    )

    return RedirectResponse(
        url="/admin/peers",
        status_code=302,
    )
# =====================================================
# Delete Peer
# =====================================================

@router.get(
    "/peers/{peer_id}/delete",
)
async def delete_peer(
    peer_id: int,
    request: Request,
    service: AdminPeerService = Depends(get_admin_peer_service),
):
    """
    Delete peer.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    await service.delete_peer(
        peer_id
    )

    return RedirectResponse(
        url="/admin/peers",
        status_code=302,
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