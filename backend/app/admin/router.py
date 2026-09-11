"""
Admin dashboard and authentication router.
"""

from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    RedirectResponse,
    Response,
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.auth import (
    is_admin_authenticated,
    login_admin,
    logout_admin,
)
from backend.app.db.database import get_db
from backend.app.services.admin_peer import AdminPeerService
from backend.app.services.admin_user import AdminUserService
from backend.app.services.config_generator import ConfigGeneratorService
from backend.app.services.dashboard import DashboardService
from backend.app.services.traffic import TrafficService
from backend.app.services.activity_log import ActivityLogService
from backend.app.services.admin_logging import log_admin_action
from backend.app.core.config import settings
from backend.app.services.auth import AuthService
router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


templates = Jinja2Templates(
    directory="backend/app/templates",
)


@router.get("/whatsapp-proxy", response_class=HTMLResponse)
async def whatsapp_proxy_page(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    host = settings.WG_ENDPOINT.split(":", 1)[0]
    return templates.TemplateResponse(
        request=request,
        name="admin/whatsapp_proxy.html",
        context={"request": request, "proxy_host": host, "proxy_port": "5222"},
    )


def _parse_optional_gb(value: str | None) -> float | None:
    """Treat an empty HTML number field as an unlimited traffic quota."""
    if value is None or not value.strip():
        return None
    amount = float(value)
    if amount < 0:
        raise ValueError("سقف حجم نمی‌تواند منفی باشد")
    return amount


# =====================================================
# Dependencies
# =====================================================


async def get_dashboard_service(
    session: AsyncSession = Depends(get_db),
) -> DashboardService:

    return DashboardService(session)


async def get_admin_user_service(
    session: AsyncSession = Depends(get_db),
) -> AdminUserService:

    return AdminUserService(session)


async def get_admin_peer_service(
    session: AsyncSession = Depends(get_db),
) -> AdminPeerService:

    return AdminPeerService(session)


async def get_admin_traffic_service(
    session: AsyncSession = Depends(get_db),
) -> TrafficService:

    return TrafficService(session)


async def get_admin_activity_log_service(
    session: AsyncSession = Depends(get_db),
) -> ActivityLogService:

    return ActivityLogService(session)

async def get_config_service() -> ConfigGeneratorService:

    return ConfigGeneratorService(
        endpoint=settings.AWG_ENDPOINT,
        server_public_key=settings.AWG_SERVER_PUBLIC_KEY,
    )


# =====================================================
# Download AmneziaWG Config
# =====================================================


@router.get(
    "/peers/{peer_id}/config",
)
async def download_peer_config(
    peer_id: int,
    request: Request,
    peer_service: AdminPeerService = Depends(
        get_admin_peer_service
    ),
    config_service: ConfigGeneratorService = Depends(
        get_config_service
    ),
):

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    peer = await peer_service.get_peer(peer_id)

    if not peer:
        return RedirectResponse(
            url="/admin/peers",
            status_code=302,
        )

    config = config_service.generate(peer)

    return Response(
        content=config,
        media_type="text/plain",
        headers={
            "Content-Disposition":
            f"attachment; filename={peer.name}.conf"
        },
    )


# =====================================================
# Login
# =====================================================


@router.get(
    "/login",
    response_class=HTMLResponse,
)
async def login_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "request": request,
            "error": None,
        },
    )


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_db),
):

    user = await AuthService(session).authenticate(username, password)
    if user is not None and user.is_superuser:

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
    service: DashboardService = Depends(
        get_dashboard_service
    ),
):

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
    service: AdminUserService = Depends(
        get_admin_user_service
    ),
):

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


@router.get("/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    request: Request,
    service: AdminUserService = Depends(
        get_admin_user_service
    ),
):

    if not is_admin_authenticated(request):

        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )


    await service.delete_user(user_id)


    return RedirectResponse(
        url="/admin/users",
        status_code=302,
    )


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_page(user_id: int, request: Request, service: AdminUserService = Depends(get_admin_user_service)):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    user = await service.get_user(user_id)
    if not user:
        return RedirectResponse(url="/admin/users", status_code=302)
    return templates.TemplateResponse(request=request, name="admin/edit_user.html", context={"request": request, "user": user, "error": None})


@router.post("/users/{user_id}/edit")
async def edit_user(user_id: int, request: Request, username: str = Form(...), password: str = Form(""), service: AdminUserService = Depends(get_admin_user_service)):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    try:
        user = await service.update_user(user_id, username.strip(), password)
        if not user:
            return RedirectResponse(url="/admin/users", status_code=302)
    except ValueError as exc:
        user = await service.get_user(user_id)
        return templates.TemplateResponse(request=request, name="admin/edit_user.html", context={"request": request, "user": user, "error": str(exc)}, status_code=400)
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get(
    "/users/create",
    response_class=HTMLResponse,
)
async def create_user_page(
    request: Request,
):

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

@router.post("/users/create")
async def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    expires_at: str | None = Form(None),
    traffic_limit_gb: str | None = Form(None),
    rate_limit_mbps: int = Form(15),
    protocol: str = Form("amneziawg"),
    service: AdminUserService = Depends(
        get_admin_user_service
    ),
    peer_service: AdminPeerService = Depends(
        get_admin_peer_service
    ),
):

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    try:
        expires = datetime.fromisoformat(expires_at) if expires_at else None
        if rate_limit_mbps < 1 or rate_limit_mbps > 15:
            raise ValueError("سقف سرعت باید بین 1 تا 15 مگابیت باشد")
        traffic_limit_gb = _parse_optional_gb(traffic_limit_gb)
        traffic_limit_bytes = (
            int(traffic_limit_gb * 1024**3)
            if traffic_limit_gb is not None and traffic_limit_gb > 0
            else None
        )
    except (TypeError, ValueError) as exc:
        return templates.TemplateResponse(
            request=request,
            name="admin/create_user.html",
            context={"request": request, "error": str(exc)},
            status_code=400,
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

    try:
        peer = await peer_service.create_peer(
            user_id=user.id,
            name=username,
            expires_at=expires,
            traffic_limit_bytes=traffic_limit_bytes,
            rate_limit_mbps=rate_limit_mbps,
            protocol=protocol,
        )
    except (ValueError, RuntimeError) as exc:
        # Do not leave an account that can never receive a usable VPN profile.
        await service.delete_user(user.id)
        return templates.TemplateResponse(
            request=request,
            name="admin/create_user.html",
            context={"request": request, "error": str(exc)},
            status_code=400,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/peer_created.html",
        context={
            "request": request,
            "peer": peer,
            "traffic_limit_gb": traffic_limit_gb,
        },
    )


# =====================================================
# Peers
# =====================================================
# =====================================================
# Peers
# =====================================================

@router.get(
    "/peers",
    response_class=HTMLResponse,
)
async def peers(
    request: Request,
    service: AdminPeerService = Depends(
        get_admin_peer_service
    ),
):

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
):

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
            "error": None,
        },
    )


@router.get("/peers/import", response_class=HTMLResponse)
async def import_peer_page(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin/import_peer.html",
        context={"request": request, "error": None},
    )


@router.post("/peers/import")
async def import_peer(
    request: Request,
    username: str = Form(...),
    name: str = Form(...),
    config: UploadFile = File(...),
    service: AdminPeerService = Depends(get_admin_peer_service),
):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    if not config.filename or not config.filename.lower().endswith(".conf"):
        return templates.TemplateResponse(
            request=request,
            name="admin/import_peer.html",
            context={"request": request, "error": "فقط فایل .conf مجاز است"},
            status_code=400,
        )
    try:
        text = (await config.read()).decode("utf-8")
        await service.import_config(username, name, text)
    except (UnicodeDecodeError, ValueError, RuntimeError) as exc:
        return templates.TemplateResponse(
            request=request,
            name="admin/import_peer.html",
            context={"request": request, "error": str(exc)},
            status_code=400,
        )
    return RedirectResponse(url="/admin/peers", status_code=302)
@router.post("/peers/create")
async def create_peer(
    request: Request,
    user_id: int = Form(...),
    name: str = Form(...),
    expires_at: str | None = Form(None),
    traffic_limit_gb: str | None = Form(None),
    rate_limit_mbps: int = Form(15),
    protocol: str = Form("amneziawg"),
    service: AdminPeerService = Depends(
        get_admin_peer_service
    ),
):
    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    if expires_at:
        expires_at = datetime.fromisoformat(
            expires_at
        )
    else:
        expires_at = None

    try:
        traffic_limit_gb = _parse_optional_gb(traffic_limit_gb)
        if rate_limit_mbps < 1 or rate_limit_mbps > 15:
            raise ValueError("سقف سرعت باید بین 1 تا 15 مگابیت باشد")
        traffic_limit_bytes = (
            int(traffic_limit_gb * 1024**3)
            if traffic_limit_gb is not None and traffic_limit_gb > 0
            else None
        )
        peer = await service.create_peer(
            user_id=user_id,
            name=name,
            expires_at=expires_at,
            traffic_limit_bytes=traffic_limit_bytes,
            rate_limit_mbps=rate_limit_mbps,
            protocol=protocol,
        )
    except (ValueError, RuntimeError) as exc:
        return templates.TemplateResponse(
            request=request,
            name="admin/create_peer.html",
            context={"request": request, "error": str(exc)},
            status_code=400,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/peer_created.html",
        context={
            "request": request,
            "peer": peer,
            "traffic_limit_gb": traffic_limit_gb,
        },
    )

@router.get("/peers/{peer_id}/delete")
async def delete_peer(
    peer_id: int,
    request: Request,
    service: AdminPeerService = Depends(
        get_admin_peer_service
    ),
):

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    try:
        await service.delete_peer(peer_id)
    except Exception as exc:
        # Never render a blank 500 page for an admin action. The operation is
        # rolled back by the service and the error is shown on the list page.
        return RedirectResponse(
            url=f"/admin/peers?error={quote(str(exc))}",
            status_code=303,
        )
    return RedirectResponse(url="/admin/peers", status_code=303)


@router.post("/peers/{peer_id}/renew")
async def renew_peer(
    peer_id: int,
    request: Request,
    days: int = Form(30),
    traffic_limit_gb: str | None = Form(None),
    service: AdminPeerService = Depends(get_admin_peer_service),
):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    try:
        traffic_limit_gb = _parse_optional_gb(traffic_limit_gb)
        await service.extend_peer(peer_id, days, traffic_limit_gb)
    except (ValueError, RuntimeError) as exc:
        return RedirectResponse(url=f"/admin/peers?error={exc}", status_code=303)
    return RedirectResponse(url="/admin/peers", status_code=302)


@router.get("/peers/{peer_id}/extend/{days}")
async def extend_peer_legacy(
    peer_id: int,
    days: int,
    request: Request,
    service: AdminPeerService = Depends(get_admin_peer_service),
):
    """Compatibility route for the existing +30-day links in the panel."""
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    try:
        await service.extend_peer(peer_id, days)
    except (ValueError, RuntimeError) as exc:
        return RedirectResponse(
            url=f"/admin/peers?error={quote(str(exc))}",
            status_code=303,
        )
    return RedirectResponse(url="/admin/peers", status_code=303)

# =====================================================
# Logout
# =====================================================


@router.get("/logout")
async def logout(
    request: Request,
):

    logout_admin(request)

    return RedirectResponse(
        url="/admin/login",
        status_code=302,
    )
@router.get(
    "/peers/{peer_id}/qr",
)
async def download_peer_qr(
    peer_id: int,
    request: Request,
    peer_service: AdminPeerService = Depends(
        get_admin_peer_service
    ),
    config_service: ConfigGeneratorService = Depends(
        get_config_service
    ),
):
    """
    Download peer QR code.
    """

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    peer = await peer_service.get_peer(peer_id)

    if not peer:
        return RedirectResponse(
            url="/admin/peers",
            status_code=302,
        )

    qr_path = config_service.generate_qr(peer)

    return FileResponse(
        qr_path,
        media_type="image/png",
        filename=f"{peer.name}.png",
    )







# =====================================================
# ADMIN TRAFFIC
# =====================================================

@router.get(
    "/traffic",
    response_class=HTMLResponse,
)
async def admin_traffic(
    request: Request,
    session: AsyncSession = Depends(get_db),
):

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    service = TrafficService(session)

    traffic = await service.get_all()

    return templates.TemplateResponse(
        request=request,
        name="admin/traffic.html",
        context={
            "request": request,
            "traffic": traffic,
            "total": len(traffic),
        },
    )


@router.get("/traffic/{traffic_id}/delete")
async def delete_admin_traffic(
    traffic_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db),
):

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    service = TrafficService(session)

    await service.delete(traffic_id)

    return RedirectResponse(
        url="/admin/traffic",
        status_code=302,
    )


# =====================================================
# ADMIN ACTIVITY LOGS
# =====================================================

@router.get(
    "/activity-logs",
    response_class=HTMLResponse,
)
async def admin_activity_logs(
    request: Request,
    session: AsyncSession = Depends(get_db),
):

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    service = ActivityLogService(session)

    logs = await service.get_all()

    return templates.TemplateResponse(
        request=request,
        name="admin/activity_logs.html",
        context={
            "request": request,
            "logs": logs,
            "total": len(logs),
        },
    )


@router.get("/activity-logs/{log_id}/delete")
async def delete_admin_activity_log(
    log_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db),
):

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    service = ActivityLogService(session)

    await service.delete(log_id)

    return RedirectResponse(
        url="/admin/activity-logs",
        status_code=302,
    )



@router.get(
    "/about",
    response_class=HTMLResponse,
)
async def about(
    request: Request,
):
    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/about.html",
        context={
            "request": request,
        },
    )
