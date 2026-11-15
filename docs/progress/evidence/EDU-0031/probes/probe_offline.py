"""Offline probes (no database). Run from backend/ with backend/.venv python.

A. CORS: Settings accepts cors_origins=["*"]; Starlette then reflects any Origin
   together with Access-Control-Allow-Credentials when a Cookie header is sent.
B. Argon2id cost per verify (runs synchronously inside `async def login`).
C. LoginRateLimiter LRU eviction: flooding max_keys distinct keys drops a blocked
   victim key, resetting its window.
Synthetic values only.
"""
import time

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.modules.auth.rate_limit import LoginRateLimiter
from app.modules.auth.services import hash_password, verify_password


def probe_cors() -> None:
    app = create_app(Settings(cors_origins=["*"], _env_file=None))
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/health/live",
            headers={"Origin": "https://attacker.example", "Cookie": "eduops_session=x"},
        )
    print(
        "A. cors_origins=['*'] accepted by Settings; ACAO =",
        response.headers.get("access-control-allow-origin"),
        "| ACAC =",
        response.headers.get("access-control-allow-credentials"),
    )


def probe_argon2() -> None:
    stored = hash_password("Synthetic-Password-123!")
    samples = []
    for _ in range(5):
        start = time.perf_counter()
        verify_password("wrong-password", stored)
        samples.append((time.perf_counter() - start) * 1000)
    print("B. argon2 verify ms:", [round(value, 1) for value in samples])


def probe_rate_limiter_eviction() -> None:
    limiter = LoginRateLimiter(limit=10, window_seconds=60)
    victim = "victim-key"
    for _ in range(10):
        limiter.record_failure(victim)
    blocked_before = limiter.check(victim)
    for index in range(limiter.max_keys):
        limiter.record_failure(f"flood-{index}")
    blocked_after = limiter.check(victim)
    print(
        "C. victim retry_after before flood =",
        blocked_before,
        "| after",
        limiter.max_keys,
        "distinct keys =",
        blocked_after,
    )


if __name__ == "__main__":
    probe_cors()
    probe_argon2()
    probe_rate_limiter_eviction()
