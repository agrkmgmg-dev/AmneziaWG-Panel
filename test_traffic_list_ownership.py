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


def test_traffic_list_ownership() -> None:
    suffix = uuid.uuid4().hex[:8]

    user_a_username = f"traffic-list-a-{suffix}"
    user_b_username = f"traffic-list-b-{suffix}"

    user_a_password = f"TrafficA-{suffix}12345!"
    user_b_password = f"TrafficB-{suffix}12345!"

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
        f"traffic-list-peer-a-{suffix}",
        "10.0.0.41",
    )

    peer_b_id = create_peer(
        admin_headers,
        user_b_id,
        f"traffic-list-peer-b-{suffix}",
        "10.0.0.42",
    )

    traffic_a_id = create_traffic(
        admin_headers,
        peer_a_id,
        upload_bytes=1000,
        download_bytes=2000,
    )

    traffic_b_id = create_traffic(
        admin_headers,
        peer_b_id,
        upload_bytes=3000,
        download_bytes=4000,
    )

    # ========================================================
    # User A must see only own traffic
    # ========================================================

    response = client.get(
        "/api/v1/traffic",
        headers=user_a_headers,
    )

    assert response.status_code == 200

    traffic_ids = {
        item["id"]
        for item in response.json()
    }

    assert traffic_a_id in traffic_ids
    assert traffic_b_id not in traffic_ids

    # ========================================================
    # User B must see only own traffic
    # ========================================================

    response = client.get(
        "/api/v1/traffic",
        headers=user_b_headers,
    )

    assert response.status_code == 200

    traffic_ids = {
        item["id"]
        for item in response.json()
    }

    assert traffic_b_id in traffic_ids
    assert traffic_a_id not in traffic_ids

    # ========================================================
    # Admin can see both
    # ========================================================

    response = client.get(
        "/api/v1/traffic",
        headers=admin_headers,
    )

    assert response.status_code == 200

    traffic_ids = {
        item["id"]
        for item in response.json()
    }

    assert traffic_a_id in traffic_ids
    assert traffic_b_id in traffic_ids
