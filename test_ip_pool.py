from backend.app.services.ip_pool import IPPoolService


def test_get_available_ips():
    pool = IPPoolService(
        subnet="10.0.0.0/29",
        server_ip="10.0.0.1",
    )

    available = pool.get_available_ips(
        [
            "10.0.0.2/32",
            "10.0.0.3",
        ]
    )

    assert "10.0.0.1/32" not in available
    assert "10.0.0.2/32" not in available
    assert "10.0.0.3/32" not in available

    assert "10.0.0.4/32" in available
    assert "10.0.0.5/32" in available


def test_get_next_ip():
    pool = IPPoolService(
        subnet="10.0.0.0/29",
        server_ip="10.0.0.1",
    )

    next_ip = pool.get_next_ip(
        [
            "10.0.0.2/32",
            "10.0.0.3/32",
        ]
    )

    assert next_ip == "10.0.0.4/32"


def test_get_next_ip_skips_used_ips():
    pool = IPPoolService(
        subnet="10.0.0.0/29",
        server_ip="10.0.0.1",
    )

    used_ips = [
        "10.0.0.2/32",
        "10.0.0.3/32",
        "10.0.0.4/32",
    ]

    next_ip = pool.get_next_ip(used_ips)

    assert next_ip == "10.0.0.5/32"


def test_ip_pool_statistics():
    pool = IPPoolService(
        subnet="10.0.0.0/29",
        server_ip="10.0.0.1",
    )

    stats = pool.get_statistics(
        [
            "10.0.0.2/32",
            "10.0.0.3/32",
        ]
    )

    assert stats["subnet"] == "10.0.0.0/29"
    assert stats["total"] == 6
    assert stats["used"] == 2
    assert stats["available"] == 4


def test_ip_pool_exhausted():
    pool = IPPoolService(
        subnet="10.0.0.0/30",
        server_ip="10.0.0.1",
    )

    used_ips = [
        "10.0.0.2/32",
    ]

    try:
        pool.get_next_ip(used_ips)
        assert False, "Expected IP pool exhaustion"
    except RuntimeError as exc:
        assert str(exc) == "IP pool exhausted"