import uuid

from test_auth import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    client,
    create_user,
    login,
)

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
        },
    )

    assert response.status_code in (200, 201), response.text
    return response.json()["id"]


def create_traffic(
    headers: dict,
    peer_id: int,
    upload_bytes: int = 100,
    download_bytes: int = 200,
) -> int:
    response = client.post(
        "/api/v1/traffic",
        headers=headers,
        json={
            "peer_id": peer_id,
            "upload_bytes": upload_bytes,
            "download_bytes": download_bytes,
        },
    )

    assert response.status_code in (200, 201), response.text
    return response.json()["id"]


def test_traffic_ownership_access_control() -> None:
    suffix = uuid.uuid4().hex[:8]

    user_a_username = f"traffic-owner-a-{suffix}"
    user_b_username = f"traffic-owner-b-{suffix}"

    user_a_password = f"TrafficA-{suffix}12345!"
    user_b_password = f"TrafficB-{suffix}12345!"

    peer_a_name = f"traffic-peer-a-{suffix}"
    peer_b_name = f"traffic-peer-b-{suffix}"

    # ============================================================
    # SETUP
    # ============================================================

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
        "10.0.0.31",
    )

    peer_b_id = create_peer(
        admin_headers,
        user_b_id,
        peer_b_name,
        "10.0.0.32",
    )

    traffic_a_id = create_traffic(
        admin_headers,
        peer_a_id,
    )

    traffic_b_id = create_traffic(
        admin_headers,
        peer_b_id,
    )

    # ============================================================
    # A. GET PEER USAGE
    # ============================================================

    # User A -> own peer usage = 200
    response = client.get(
        f"/api/v1/traffic/peer/{peer_a_id}/usage",
        headers=user_a_headers,
    )
    assert response.status_code == 200

    # User A -> User B peer usage = 403
    response = client.get(
        f"/api/v1/traffic/peer/{peer_b_id}/usage",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    # User B -> own peer usage = 200
    response = client.get(
        f"/api/v1/traffic/peer/{peer_b_id}/usage",
        headers=user_b_headers,
    )
    assert response.status_code == 200

    # User B -> User A peer usage = 403
    response = client.get(
        f"/api/v1/traffic/peer/{peer_a_id}/usage",
        headers=user_b_headers,
    )
    assert response.status_code == 403

    # Admin -> both peers = 200
    response = client.get(
        f"/api/v1/traffic/peer/{peer_a_id}/usage",
        headers=admin_headers,
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/v1/traffic/peer/{peer_b_id}/usage",
        headers=admin_headers,
    )
    assert response.status_code == 200

    # ============================================================
    # B. GET PEER LIMIT
    # ============================================================

    response = client.get(
        f"/api/v1/traffic/peer/{peer_a_id}/limit/1000",
        headers=user_a_headers,
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/v1/traffic/peer/{peer_b_id}/limit/1000",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    response = client.get(
        f"/api/v1/traffic/peer/{peer_b_id}/limit/1000",
        headers=user_b_headers,
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/v1/traffic/peer/{peer_a_id}/limit/1000",
        headers=user_b_headers,
    )
    assert response.status_code == 403

    response = client.get(
        f"/api/v1/traffic/peer/{peer_a_id}/limit/1000",
        headers=admin_headers,
    )
    assert response.status_code == 200

    # ============================================================
    # C. GET TRAFFIC RECORD
    # ============================================================

    response = client.get(
        f"/api/v1/traffic/{traffic_a_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == traffic_a_id

    response = client.get(
        f"/api/v1/traffic/{traffic_b_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    response = client.get(
        f"/api/v1/traffic/{traffic_b_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/v1/traffic/{traffic_a_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 403

    response = client.get(
        f"/api/v1/traffic/{traffic_a_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200

    # ============================================================
    # D. CREATE TRAFFIC
    # ============================================================

    # User A -> own peer = 201
    response = client.post(
        "/api/v1/traffic",
        headers=user_a_headers,
        json={
            "peer_id": peer_a_id,
            "upload_bytes": 10,
            "download_bytes": 20,
        },
    )
    assert response.status_code == 201

    # User A -> User B peer = 403
    response = client.post(
        "/api/v1/traffic",
        headers=user_a_headers,
        json={
            "peer_id": peer_b_id,
            "upload_bytes": 10,
            "download_bytes": 20,
        },
    )
    assert response.status_code == 403

    # User B -> own peer = 201
    response = client.post(
        "/api/v1/traffic",
        headers=user_b_headers,
        json={
            "peer_id": peer_b_id,
            "upload_bytes": 10,
            "download_bytes": 20,
        },
    )
    assert response.status_code == 201

    # User B -> User A peer = 403
    response = client.post(
        "/api/v1/traffic",
        headers=user_b_headers,
        json={
            "peer_id": peer_a_id,
            "upload_bytes": 10,
            "download_bytes": 20,
        },
    )
    assert response.status_code == 403

    # ============================================================
    # E. DELETE TRAFFIC
    # ============================================================

    response = client.delete(
        f"/api/v1/traffic/{traffic_a_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 204

    response = client.delete(
        f"/api/v1/traffic/{traffic_b_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 403

    # Admin can delete remaining traffic
    response = client.delete(
        f"/api/v1/traffic/{traffic_b_id}",
        headers=admin_headers,
    )
    assert response.status_code == 204
