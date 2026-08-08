from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

USERNAME = "admin"
PASSWORD = "Admin123!"

TEST_USERNAME = "testuser_e2e"
TEST_PASSWORD = "Test12345!"


def test_user_crud_flow() -> None:
    print("=" * 60)
    print("User API E2E Test")
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

    assert access_token

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    print("PASS: Login")

    # 2. Get users
    response = client.get(
        "/api/v1/users",
        headers=headers,
    )

    print(f"\n[2] GET /users => {response.status_code}")
    print(response.json())

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    print("PASS: Get users")

    # 3. Create user
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
        },
    )

    print(f"\n[3] POST /users => {response.status_code}")
    print(response.json())

    assert response.status_code == 201

    created_user = response.json()

    user_id = created_user["id"]

    assert created_user["username"] == TEST_USERNAME
    assert created_user["is_active"] is True

    print("PASS: Create user")

    # 4. Get created user
    response = client.get(
        f"/api/v1/users/{user_id}",
        headers=headers,
    )

    print(
        f"\n[4] GET /users/{user_id} => "
        f"{response.status_code}"
    )
    print(response.json())

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == TEST_USERNAME

    print("PASS: Get user by ID")

    # 5. Update username
    updated_username = "testuser_updated"

    response = client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers,
        json={
            "username": updated_username,
        },
    )

    print(
        f"\n[5] PATCH /users/{user_id} => "
        f"{response.status_code}"
    )
    print(response.json())

    assert response.status_code == 200
    assert response.json()["username"] == updated_username

    print("PASS: Update username")

    # 6. Update password
    response = client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers,
        json={
            "password": "NewTest12345!",
        },
    )

    print(
        f"\n[6] PATCH password => "
        f"{response.status_code}"
    )

    assert response.status_code == 200

    print("PASS: Update password")

    # 7. Deactivate user
    response = client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers,
        json={
            "is_active": False,
        },
    )

    print(
        f"\n[7] PATCH is_active => "
        f"{response.status_code}"
    )
    print(response.json())

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    print("PASS: Update active status")

    # 8. Duplicate username
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "username": updated_username,
            "password": TEST_PASSWORD,
        },
    )

    print(
        f"\n[8] Duplicate username => "
        f"{response.status_code}"
    )

    if response.content:
        print(response.json())

    assert response.status_code == 409

    print("PASS: Duplicate username rejected")

    # 9. Delete user
    response = client.delete(
        f"/api/v1/users/{user_id}",
        headers=headers,
    )

    print(
        f"\n[9] DELETE /users/{user_id} => "
        f"{response.status_code}"
    )

    assert response.status_code == 204

    print("PASS: Delete user")

    # 10. Verify deletion
    response = client.get(
        f"/api/v1/users/{user_id}",
        headers=headers,
    )

    print(
        f"\n[10] GET deleted user => "
        f"{response.status_code}"
    )

    if response.content:
        print(response.json())

    assert response.status_code == 404

    print("PASS: Deleted user returns 404")

    print("\n" + "=" * 60)
    print("ALL USER API TESTS PASSED")
    print("=" * 60)