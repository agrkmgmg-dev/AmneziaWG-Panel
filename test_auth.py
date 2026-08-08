from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

USERNAME = "admin"
PASSWORD = "Admin123!"


def test_authentication_flow():
    print("=" * 60)
    print("Authentication E2E Test")
    print("=" * 60)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": USERNAME,
            "password": PASSWORD,
        },
    )

    print(f"\n[1] Login => {response.status_code}")
    assert response.status_code == 200

    tokens = response.json()

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    assert access_token
    assert refresh_token
    assert tokens["token_type"] == "bearer"

    print("PASS: Login")

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    print(f"\n[2] /me => {response.status_code}")
    assert response.status_code == 200
    assert response.json()["username"] == USERNAME

    print("PASS: Access token /me")

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    print(f"\n[3] Refresh => {response.status_code}")
    assert response.status_code == 200

    refreshed = response.json()

    new_access_token = refreshed["access_token"]
    new_refresh_token = refreshed["refresh_token"]

    assert new_access_token
    assert new_refresh_token

    print("PASS: Refresh token")

    new_headers = {
        "Authorization": f"Bearer {new_access_token}",
    }

    response = client.get(
        "/api/v1/auth/me",
        headers=new_headers,
    )

    print(
        f"\n[4] /me with refreshed token => "
        f"{response.status_code}"
    )

    assert response.status_code == 200

    print("PASS: Refreshed access token")

    response = client.post(
        "/api/v1/auth/logout",
        headers=new_headers,
    )

    print(f"\n[5] Logout => {response.status_code}")

    assert response.status_code in (200, 204)

    if response.status_code != 204:
        print(response.json())

    print("PASS: Logout / Revocation")

    response = client.get(
        "/api/v1/auth/me",
        headers=new_headers,
    )

    print(
        f"\n[6] Revoked token /me => "
        f"{response.status_code}"
    )

    assert response.status_code == 401

    print("PASS: Revoked access token rejected")

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalid-token",
        },
    )

    print(
        f"\n[7] Invalid refresh token => "
        f"{response.status_code}"
    )

    assert response.status_code == 401

    print("PASS: Invalid refresh token rejected")

    print("\n" + "=" * 60)
    print("ALL AUTHENTICATION TESTS PASSED")
    print("=" * 60)
