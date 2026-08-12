from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

USERNAME = "admin"
PASSWORD = "Admin123!"


def test_peer_api_flow():
    print("=" * 60)
    print("Peer API E2E Test")
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

    # 2. Get peers
    response = client.get(
        "/api/v1/peers",
        headers=headers,
    )

    print(f"\n[2] GET /peers => {response.status_code}")

    if response.content:
        print(response.json())

    assert response.status_code == 200

    print("PASS: Get peers")

    # 3. Create peer
    peer_data = {
        "user_id": 1,
        "name": "test-peer",
        "address": "10.0.0.10",
        "expires_at": None,
    }

    response = client.post(
        "/api/v1/peers",
        headers=headers,
        json=peer_data,
    )

    print(f"\n[3] POST /peers => {response.status_code}")

    if response.content:
        print(response.json())

    assert response.status_code == 201

    peer = response.json()
    peer_id = peer["id"]

    assert peer["name"] == "test-peer"
    assert peer["user_id"] == 1
    assert peer["address"] == "10.0.0.10"

    # WireGuard public key
    assert "public_key" in peer
    assert peer["public_key"]
    assert peer["public_key"] != "pending"
    assert len(peer["public_key"]) == 44

    # Private key must never be exposed
    assert "private_key" not in peer

    print("PASS: Create peer")
    print(f"Public Key: {peer['public_key']}")
    print("PASS: Private key is not exposed")

    # 4. Get created peer
    response = client.get(
        f"/api/v1/peers/{peer_id}",
        headers=headers,
    )

    print(
        f"\n[4] GET /peers/{peer_id} => "
        f"{response.status_code}"
    )

    if response.content:
        print(response.json())

    assert response.status_code == 200

    peer = response.json()

    assert peer["id"] == peer_id
    assert peer["name"] == "test-peer"
    assert peer["public_key"]
    assert peer["public_key"] != "pending"
    assert len(peer["public_key"]) == 44

    assert "private_key" not in peer

    print("PASS: Get peer")
    print("PASS: Public key persisted")
    print("PASS: Private key remains hidden")

    # 5. Update peer
    response = client.put(
        f"/api/v1/peers/{peer_id}",
        headers=headers,
        json={
            "name": "test-peer-updated",
            "is_active": False,
            "expires_at": None,
        },
    )

    print(
        f"\n[5] PUT /peers/{peer_id} => "
        f"{response.status_code}"
    )

    if response.content:
        print(response.json())

    assert response.status_code == 200

    peer = response.json()

    assert peer["name"] == "test-peer-updated"
    assert peer["is_active"] is False
    assert peer["public_key"]
    assert peer["public_key"] != "pending"
    assert len(peer["public_key"]) == 44

    print("PASS: Update peer")
    print("PASS: Public key preserved")

    # 6. Duplicate peer name
    response = client.post(
        "/api/v1/peers",
        headers=headers,
        json={
            "user_id": 1,
            "name": "test-peer-updated",
            "address": "10.0.0.11",
            "expires_at": None,
        },
    )

    print(
        f"\n[6] Duplicate peer => "
        f"{response.status_code}"
    )

    if response.content:
        print(response.json())

    assert response.status_code == 409

    print("PASS: Duplicate peer rejected")

    # 7. Delete peer
    response = client.delete(
        f"/api/v1/peers/{peer_id}",
        headers=headers,
    )

    print(
        f"\n[7] DELETE /peers/{peer_id} => "
        f"{response.status_code}"
    )

    assert response.status_code == 204

    print("PASS: Delete peer")

    # 8. Deleted peer must not exist
    response = client.get(
        f"/api/v1/peers/{peer_id}",
        headers=headers,
    )

    print(
        f"\n[8] Deleted peer GET => "
        f"{response.status_code}"
    )

    if response.content:
        print(response.json())

    assert response.status_code == 404

    print("PASS: Deleted peer rejected")

    # 9. Non-existing peer
    response = client.get(
        "/api/v1/peers/999999",
        headers=headers,
    )

    print(
        f"\n[9] Non-existing peer => "
        f"{response.status_code}"
    )

    if response.content:
        print(response.json())

    assert response.status_code == 404

    print("PASS: 404 handling")

    print("\n" + "=" * 60)
    print("ALL PEER API TESTS PASSED")
    print("=" * 60)
