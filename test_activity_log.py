from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

USERNAME = "admin"
PASSWORD = "Admin123!"


def test_activity_log_api_flow() -> None:
    print("=" * 60)
    print("Activity Log API E2E Test")
    print("=" * 60)

    # 1. Login
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

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    print("PASS: Login")

    # 2. Get activity logs
    response = client.get(
        "/api/v1/activity-logs",
        headers=headers,
    )

    print(
        f"\n[2] GET /activity-logs => "
        f"{response.status_code}"
    )
    print(response.json())

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    print("PASS: Get activity logs")

    # 3. Create activity log
    response = client.post(
        "/api/v1/activity-logs",
        headers=headers,
        json={
            "user_id": 1,
            "action": "test",
            "description": "Activity log E2E test",
        },
    )

    print(
        f"\n[3] POST /activity-logs => "
        f"{response.status_code}"
    )
    print(response.json())

    assert response.status_code == 201

    created = response.json()
    log_id = created["id"]

    assert created["user_id"] == 1
    assert created["action"] == "test"

    print("PASS: Create activity log")

    # 4. Get activity log by ID
    response = client.get(
        f"/api/v1/activity-logs/{log_id}",
        headers=headers,
    )

    print(
        f"\n[4] GET /activity-logs/{log_id} => "
        f"{response.status_code}"
    )
    print(response.json())

    assert response.status_code == 200
    assert response.json()["id"] == log_id

    print("PASS: Get activity log")

    # 5. Get latest activity logs
    response = client.get(
        "/api/v1/activity-logs/latest?limit=10",
        headers=headers,
    )

    print(
        f"\n[5] GET /activity-logs/latest => "
        f"{response.status_code}"
    )
    print(response.json())

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    print("PASS: Get latest activity logs")

    # 6. Delete activity log
    response = client.delete(
        f"/api/v1/activity-logs/{log_id}",
        headers=headers,
    )

    print(
        f"\n[6] DELETE /activity-logs/{log_id} => "
        f"{response.status_code}"
    )

    assert response.status_code == 204

    print("PASS: Delete activity log")

    # 7. Verify deletion
    response = client.get(
        f"/api/v1/activity-logs/{log_id}",
        headers=headers,
    )

    print(
        f"\n[7] GET deleted activity log => "
        f"{response.status_code}"
    )

    assert response.status_code == 404

    print("PASS: Deleted activity log rejected")

    print("\n" + "=" * 60)
    print("ALL ACTIVITY LOG TESTS PASSED")
    print("=" * 60)