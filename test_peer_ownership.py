import uuid

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123!"


def login(username: str, password: str) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def create_user(
    admin_headers: dict,
    username: str,
    password: str,
) -> int:
    response = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_peer(
    headers: dict,
    user_id: int,
    name: str,
    address: str,
) -> int:
    response = client.post(
        "/api/v1/peers",
        headers=headers,
        json={
            "user_id": user_id,
            "name": name,
            "address": address,
            "expires_at": None,
        },
    )

    assert response.status_code == 201

    peer = response.json()

    assert peer["user_id"] == user_id

    return peer["id"]


def test_peer_ownership_access_control() -> None:
    suffix = uuid.uuid4().hex[:8]

    user_a_username = f"peer-owner-a-{suffix}"
    user_b_username = f"peer-owner-b-{suffix}"

    user_a_password = f"PeerA-{suffix}12345!"
    user_b_password = f"PeerB-{suffix}12345!"

    peer_a_name = f"ownership-peer-a-{suffix}"
    peer_b_name = f"ownership-peer-b-{suffix}"

    admin_headers = login(
        ADMIN_USERNAME,
        ADMIN_PASSWORD,
    )

    user_a_id = create_user(
        admin_headers,
        user_a_username,
        user_a_password,
    )

    user_b_id = create_user(
        admin_headers,
        user_b_username,
        user_b_password,
    )

    assert user_a_id != user_b_id

    user_a_headers = login(
        user_a_username,
        user_a_password,
    )

    user_b_headers = login(
        user_b_username,
        user_b_password,
    )

    peer_a_id = create_peer(
        admin_headers,
        user_a_id,
        peer_a_name,
        "10.0.0.21",
    )

    peer_b_id = create_peer(
        admin_headers,
        user_b_id,
        peer_b_name,
        "10.0.0.22",
    )

    # ============================================================
    # A. GET /peers/{peer_id}
    # ============================================================

    # 1. User A -> own peer = 200
    response = client.get(
        f"/api/v1/peers/{peer_a_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == peer_a_id

    # 2. User A -> User B peer = 403
    response = client.get(
        f"/api/v1/peers/{peer_b_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    # 3. User B -> own peer = 200
    response = client.get(
        f"/api/v1/peers/{peer_b_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == peer_b_id

    # 4. User B -> User A peer = 403
    response = client.get(
        f"/api/v1/peers/{peer_a_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 403

    # 5. Admin -> User A peer = 200
    response = client.get(
        f"/api/v1/peers/{peer_a_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200

    # ============================================================
    # B. UPDATE /peers/{peer_id}
    # ============================================================

    # 6. User A -> update own peer = 200
    response = client.put(
        f"/api/v1/peers/{peer_a_id}",
        headers=user_a_headers,
        json={
            "name": f"{peer_a_name}-updated",
        },
    )
    assert response.status_code == 200
    assert response.json()["id"] == peer_a_id

    # 7. User A -> update User B peer = 403
    response = client.put(
        f"/api/v1/peers/{peer_b_id}",
        headers=user_a_headers,
        json={
            "name": f"{peer_b_name}-blocked-a",
        },
    )
    assert response.status_code == 403

    # 8. User B -> update own peer = 200
    response = client.put(
        f"/api/v1/peers/{peer_b_id}",
        headers=user_b_headers,
        json={
            "name": f"{peer_b_name}-updated",
        },
    )
    assert response.status_code == 200
    assert response.json()["id"] == peer_b_id

    # 9. User B -> update User A peer = 403
    response = client.put(
        f"/api/v1/peers/{peer_a_id}",
        headers=user_b_headers,
        json={
            "name": f"{peer_a_name}-blocked-b",
        },
    )
    assert response.status_code == 403

    # 10. Admin -> update User A peer = 200
    response = client.put(
        f"/api/v1/peers/{peer_a_id}",
        headers=admin_headers,
        json={
            "name": f"{peer_a_name}-admin-updated",
        },
    )
    assert response.status_code == 200
    assert response.json()["id"] == peer_a_id

    # ============================================================
    # C. CONFIG /peers/{peer_id}/config
    # ============================================================

    # 11. User A -> own peer config = 200
    response = client.get(
        f"/api/v1/peers/{peer_a_id}/config",
        headers=user_a_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "attachment" in response.headers["content-disposition"]

    # 12. User A -> User B config = 403
    response = client.get(
        f"/api/v1/peers/{peer_b_id}/config",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    # 13. User B -> own peer config = 200
    response = client.get(
        f"/api/v1/peers/{peer_b_id}/config",
        headers=user_b_headers,
    )
    assert response.status_code == 200

    # 14. User B -> User A config = 403
    response = client.get(
        f"/api/v1/peers/{peer_a_id}/config",
        headers=user_b_headers,
    )
    assert response.status_code == 403

    # 15. Admin -> User A config = 200
    response = client.get(
        f"/api/v1/peers/{peer_a_id}/config",
        headers=admin_headers,
    )
    assert response.status_code == 200

    # ============================================================
    # D. QR /peers/{peer_id}/qr
    # ============================================================

    # 16. User A -> own peer QR = 200
    response = client.get(
        f"/api/v1/peers/{peer_a_id}/qr",
        headers=user_a_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")

    # 17. User A -> User B QR = 403
    response = client.get(
        f"/api/v1/peers/{peer_b_id}/qr",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    # 18. User B -> own peer QR = 200
    response = client.get(
        f"/api/v1/peers/{peer_b_id}/qr",
        headers=user_b_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")

    # 19. User B -> User A QR = 403
    response = client.get(
        f"/api/v1/peers/{peer_a_id}/qr",
        headers=user_b_headers,
    )
    assert response.status_code == 403

    # 20. Admin -> User A QR = 200
    response = client.get(
        f"/api/v1/peers/{peer_a_id}/qr",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")

    # ============================================================
    # E. DELETE /peers/{peer_id}
    # ============================================================

    # 21. User A -> delete User B peer = 403
    response = client.delete(
        f"/api/v1/peers/{peer_b_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    # 22. User B -> delete User A peer = 403
    response = client.delete(
        f"/api/v1/peers/{peer_a_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 403

    # 23. User A -> delete own peer = 204
    response = client.delete(
        f"/api/v1/peers/{peer_a_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 204

    # 24. Deleted peer -> 404
    response = client.get(
        f"/api/v1/peers/{peer_a_id}",
        headers=admin_headers,
    )
    assert response.status_code == 404

    # 25. Admin -> delete User B peer = 204
    response = client.delete(
        f"/api/v1/peers/{peer_b_id}",
        headers=admin_headers,
    )
    assert response.status_code == 204

    # 26. Deleted peer -> 404
    response = client.get(
        f"/api/v1/peers/{peer_b_id}",
        headers=admin_headers,
    )
    assert response.status_code == 404

    # ============================================================
    # F. LIST /peers
    # ============================================================

    # Create fresh peers because the previous two were deleted.
    peer_a_list_id = create_peer(
        admin_headers,
        user_a_id,
        f"{peer_a_name}-list",
        "10.0.0.31",
    )

    peer_b_list_id = create_peer(
        admin_headers,
        user_b_id,
        f"{peer_b_name}-list",
        "10.0.0.32",
    )

    # 27. User A -> GET /peers -> only own peers
    response = client.get(
        "/api/v1/peers",
        headers=user_a_headers,
    )
    assert response.status_code == 200

    peer_ids = {peer["id"] for peer in response.json()}

    assert peer_a_list_id in peer_ids
    assert peer_b_list_id not in peer_ids

    # 28. User B -> GET /peers -> only own peers
    response = client.get(
        "/api/v1/peers",
        headers=user_b_headers,
    )
    assert response.status_code == 200

    peer_ids = {peer["id"] for peer in response.json()}

    assert peer_b_list_id in peer_ids
    assert peer_a_list_id not in peer_ids

    # 29. Admin -> GET /peers -> all peers
    response = client.get(
        "/api/v1/peers",
        headers=admin_headers,
    )
    assert response.status_code == 200

    peer_ids = {peer["id"] for peer in response.json()}

    assert peer_a_list_id in peer_ids
    assert peer_b_list_id in peer_ids

    # ============================================================
    # G. GET /peers/user/{user_id}
    # ============================================================

    # 30. User A -> own user peer list = 200
    response = client.get(
        f"/api/v1/peers/user/{user_a_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 200

    peer_ids = {peer["id"] for peer in response.json()}

    assert peer_a_list_id in peer_ids
    assert peer_b_list_id not in peer_ids

    # 31. User A -> User B peer list = 403
    response = client.get(
        f"/api/v1/peers/user/{user_b_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    # 32. User B -> own user peer list = 200
    response = client.get(
        f"/api/v1/peers/user/{user_b_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 200

    peer_ids = {peer["id"] for peer in response.json()}

    assert peer_b_list_id in peer_ids
    assert peer_a_list_id not in peer_ids

    # 33. User B -> User A peer list = 403
    response = client.get(
        f"/api/v1/peers/user/{user_a_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 403

    # 34. Admin -> User A peer list = 200
    response = client.get(
        f"/api/v1/peers/user/{user_a_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200

    peer_ids = {peer["id"] for peer in response.json()}

    assert peer_a_list_id in peer_ids
    assert peer_b_list_id not in peer_ids

