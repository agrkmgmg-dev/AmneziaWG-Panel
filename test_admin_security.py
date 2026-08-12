from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_admin_pages_require_authentication() -> None:
    protected_routes = [
        "/admin/dashboard",
        "/admin/users",
        "/admin/users/create",
        "/admin/peers",
        "/admin/peers/create",
    ]

    for route in protected_routes:
        client.cookies.clear()

        response = client.get(
            route,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login"


def test_admin_peer_create_requires_authentication() -> None:
    client.cookies.clear()

    response = client.post(
        "/admin/peers/create",
        data={
            "user_id": 1,
            "name": "unauthorized-admin-peer",
            "expires_at": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"


def test_admin_user_create_page_requires_authentication() -> None:
    client.cookies.clear()

    response = client.get(
        "/admin/users/create",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"


def test_admin_user_create_requires_authentication() -> None:
    client.cookies.clear()

    response = client.post(
        "/admin/users/create",
        data={
            "username": "unauthorized-admin-user",
            "password": "Unauthorized123!",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"


def test_admin_login_success() -> None:
    client.cookies.clear()

    response = client.post(
        "/admin/login",
        data={
            "username": "admin",
            "password": "Admin123!",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/admin/dashboard"


def test_admin_dashboard_after_login() -> None:
    client.cookies.clear()

    response = client.post(
        "/admin/login",
        data={
            "username": "admin",
            "password": "Admin123!",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    response = client.get("/admin/dashboard")

    assert response.status_code == 200
