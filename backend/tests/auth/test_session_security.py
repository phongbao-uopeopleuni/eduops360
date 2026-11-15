from app.modules.auth.rate_limit import LoginRateLimiter
from app.modules.auth.session import verify_totp


class _ExplodingDeque(list[float]):
    def __getitem__(self, index):
        raise AssertionError("eviction scan exceeded its configured window cap")


def test_totp_accepts_rfc_vector_and_rejects_invalid_codes() -> None:
    secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    assert verify_totp(secret, "287082", now=59)
    assert not verify_totp(secret, "287083", now=59)
    assert not verify_totp("not-base32!", "287082", now=59)
    assert not verify_totp(secret, "12345", now=59)


def test_login_rate_limiter_blocks_then_expires_window() -> None:
    now = [100.0]
    limiter = LoginRateLimiter(
        limit=2,
        window_seconds=10,
        max_keys=2,
        clock=lambda: now[0],
    )
    assert limiter.check("account") is None
    limiter.record_failure("account")
    limiter.record_failure("account")
    assert limiter.check("account") == 11
    now[0] = 111.0
    assert limiter.check("account") is None


def test_login_rate_limiter_bounds_identity_storage_and_reset() -> None:
    limiter = LoginRateLimiter(limit=2, window_seconds=10, max_keys=2, clock=lambda: 1.0)
    limiter.record_failure("oldest")
    limiter.record_failure("middle")
    limiter.record_failure("newest")
    assert "oldest" not in limiter._windows
    assert len(limiter._windows) == 2
    limiter.reset("middle")
    assert "middle" not in limiter._windows


def test_login_rate_limiter_does_not_evict_an_already_blocked_key() -> None:
    limiter = LoginRateLimiter(limit=2, window_seconds=60, max_keys=2, clock=lambda: 1.0)
    limiter.record_failure("blocked-victim")
    limiter.record_failure("blocked-victim")
    limiter.record_failure("flood-1")
    limiter.record_failure("flood-2")
    assert limiter.check("blocked-victim") is not None
    assert len(limiter._windows) <= 2


def test_login_rate_limiter_caps_saturated_eviction_scan() -> None:
    limiter = LoginRateLimiter(
        limit=2,
        window_seconds=60,
        max_keys=3,
        eviction_scan_limit=2,
        clock=lambda: 1.0,
    )
    for key in ("blocked-a", "blocked-b", "blocked-c"):
        limiter.record_failure(key)
        limiter.record_failure(key)
    limiter._windows["blocked-c"].attempts = _ExplodingDeque([1.0, 1.0])

    limiter.record_failure("new-key")

    assert "new-key" not in limiter._windows
    assert limiter.check("blocked-a") is not None
    assert limiter.check("blocked-b") is not None
