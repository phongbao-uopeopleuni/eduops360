"""EDU-0042 review probes against the isolated PostgreSQL (synthetic data only).

Run from backend/ after sourcing ../.local/edu-0042/dsn.sh:
    PYTHONPATH=. .venv/Scripts/python.exe -B ../.local/edu-0042/probes/probe_review.py
Writes probe_review.json next to this file. Does not modify source code.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import struct
import threading
import time
from contextlib import closing
from pathlib import Path
from uuid import UUID, uuid4

import psycopg
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.event_loop import create_event_loop
from app.main import create_app
from app.modules.auth.rate_limit import LoginRateLimiter
from app.modules.auth.services import hash_password

MIGRATOR_DSN = os.environ["EDUOPS_TEST_MIGRATOR_DSN"]
RUNTIME_SQLA = os.environ["EDUOPS_TEST_RUNTIME_DSN"].replace(
    "postgresql://", "postgresql+psycopg://", 1
)
RUN = uuid4().hex[:10]
PASSWORD = "Synthetic-Password-123!"
OUT = Path(__file__).with_name("probe_review.json")
FULL = [
    "user:create",
    "user:read",
    "user:suspend",
    "user:activate",
    "user:password_reset",
    "user:grant_role",
    "user:revoke_role",
]
results: dict[str, dict] = {}


def mig():
    return closing(psycopg.connect(MIGRATOR_DSN, autocommit=True))


def create_user(label: str, *, status: str = "active") -> tuple[UUID, str]:
    user_id = uuid4()
    email = f"{label}-{RUN}@example.com"
    with mig() as c:
        c.execute(
            "INSERT INTO users (id, email, password_hash, display_name, status) "
            "VALUES (%s, %s, %s, 'Synthetic EDU-0042 Probe', %s)",
            (user_id, email, hash_password(PASSWORD), status),
        )
    return user_id, email


def create_role(label: str, codes: list[str]) -> UUID:
    role_id = uuid4()
    with mig() as c:
        c.execute(
            "INSERT INTO roles (id, code, name_vi) VALUES (%s, %s, 'Synthetic EDU-0042 role')",
            (role_id, f"edu0042_{label}_{RUN}"),
        )
        c.execute(
            "INSERT INTO role_permissions (role_id, permission_id) "
            "SELECT %s, id FROM permissions WHERE code = ANY(%s)",
            (role_id, codes),
        )
    return role_id


def grant(user_id, role_id, *, school=None, year=None) -> None:
    with mig() as c:
        c.execute(
            "INSERT INTO user_roles (id, user_id, role_id, school_id, academic_year_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (uuid4(), user_id, role_id, school, year),
        )


def app_for(**overrides):
    return create_app(
        Settings(database_url=RUNTIME_SQLA, environment="test", _env_file=None, **overrides)
    )


def client_for(app) -> TestClient:
    return TestClient(
        app,
        base_url="https://testserver",
        backend_options={"loop_factory": create_event_loop},
        raise_server_exceptions=False,
    )


def csrf(client: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": client.cookies.get("eduops_csrf")}


def login(client: TestClient, email: str, password: str = PASSWORD, **extra):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password, **extra})


def code_of(response) -> str | None:
    try:
        return response.json().get("error", {}).get("code")
    except ValueError:
        return None


def probe_reset_toctou(app) -> None:
    """F01 coverage is checked at issue time; is it re-checked when the token is redeemed?"""
    full = create_role("full", FULL)
    reset_only = create_role("resetonly", ["user:password_reset"])
    resetter_id, resetter_email = create_user("ra-resetter")
    grant(resetter_id, reset_only)
    target_id, target_email = create_user("ra-target")
    bystander_id, _ = create_user("ra-bystander")
    out: dict = {}
    with client_for(app) as resetter:
        assert login(resetter, resetter_email).status_code == 200
        issued = resetter.post(
            f"/api/v1/admin/users/{target_id}/password-reset", json={}, headers=csrf(resetter)
        )
        out["issue_reset_while_target_unprivileged_http"] = issued.status_code
        token = issued.json()["one_time_token"]
        grant(target_id, full)  # an authorised admin later promotes the target
        out["issue_reset_after_promotion_http"] = resetter.post(
            f"/api/v1/admin/users/{target_id}/password-reset", json={}, headers=csrf(resetter)
        ).status_code
        # The second issue (if denied) must not have invalidated the first token.
        accept = resetter.post(
            "/api/v1/auth/password-reset/accept",
            json={"token": token, "new_password": "Probe-Takeover-Pass-1!"},
        )
        out["redeem_old_token_after_promotion_http"] = accept.status_code
    with client_for(app) as takeover:
        out["login_as_promoted_target_http"] = login(
            takeover, target_email, "Probe-Takeover-Pass-1!"
        ).status_code
        out["as_target_read_other_user_http"] = takeover.get(
            f"/api/v1/admin/users/{bystander_id}"
        ).status_code
    with client_for(app) as resetter:
        login(resetter, resetter_email)
        out["resetter_own_read_other_user_http"] = resetter.get(
            f"/api/v1/admin/users/{bystander_id}"
        ).status_code
    results["RA_reset_token_issued_before_target_promotion"] = out


def probe_invitation_toctou(app) -> None:
    """Inviter with only user:create keeps the raw token while the pending account is granted."""
    school, year = uuid4(), uuid4()
    inviter_role = create_role("inviter", ["user:create"])
    full = create_role("full2", FULL)
    scoped_admin = create_role("scoped", ["user:read", "user:grant_role", "user:revoke_role"])
    inviter_id, inviter_email = create_user("rb-inviter")
    grant(inviter_id, inviter_role)
    admin_id, admin_email = create_user("rb-admin")
    grant(admin_id, full)
    other_id, _ = create_user("rb-other")
    invitee_email = f"rb-invitee-{RUN}@example.com"
    base = {"role_id": str(scoped_admin), "school_id": str(school), "academic_year_id": str(year)}
    out: dict = {}
    with client_for(app) as inviter:
        assert login(inviter, inviter_email).status_code == 200
        invited = inviter.post(
            "/api/v1/admin/users/invitations",
            json={"email": invitee_email, "display_name": "Probe Invitee"},
            headers=csrf(inviter),
        )
        out["invite_http"] = invited.status_code
        invitee_id = invited.json()["user"]["id"]
        raw_token = invited.json()["one_time_token"]
        out["inviter_grants_scoped_role_http"] = inviter.post(
            f"/api/v1/admin/users/{other_id}/roles", json=base, headers=csrf(inviter)
        ).status_code
    with client_for(app) as admin:
        assert login(admin, admin_email).status_code == 200
        out["admin_grants_role_to_pending_invitee_http"] = admin.post(
            f"/api/v1/admin/users/{invitee_id}/roles", json=base, headers=csrf(admin)
        ).status_code
    with client_for(app) as inviter:
        out["inviter_redeems_kept_invitation_http"] = inviter.post(
            "/api/v1/auth/invitations/accept",
            json={"token": raw_token, "password": "Probe-Inviter-Chosen-1!"},
        ).status_code
    with client_for(app) as takeover:
        out["login_as_invitee_with_inviter_password_http"] = login(
            takeover, invitee_email, "Probe-Inviter-Chosen-1!"
        ).status_code
        out["as_invitee_grant_scoped_role_http"] = takeover.post(
            f"/api/v1/admin/users/{other_id}/roles", json=base, headers=csrf(takeover)
        ).status_code
    results["RB_invitation_token_kept_while_pending_account_is_granted"] = out


def probe_ip_limiter_shared_peer() -> None:
    """Does the TẠM per-IP window (default 50/60 s) block correct logins of other accounts?"""
    app = app_for()  # default settings: 10/IP+email, 50/IP, 60 s
    victim_id, victim_email = create_user("rc-victim")
    out: dict = {}
    with client_for(app) as attacker, client_for(app) as victim:
        statuses = [
            login(attacker, f"rc-spray-{i}-{RUN}@example.com", "wrong").status_code
            for i in range(50)
        ]
        out["fifty_failed_logins_distinct_unknown_emails"] = {
            code: statuses.count(code) for code in sorted(set(statuses))
        }
        blocked = login(victim, victim_email)
        out["other_account_correct_password_same_peer_http"] = blocked.status_code
        out["other_account_correct_password_same_peer_code"] = code_of(blocked)
        out["retry_after_seconds"] = blocked.headers.get("Retry-After")
    with mig() as c:
        out["victim_account_status_after"] = c.execute(
            "SELECT status, failed_login_count FROM users WHERE id = %s", (victim_id,)
        ).fetchone()
    results["RC_per_ip_window_blocks_other_accounts_behind_same_peer"] = out


def _totp(secret: str, timestamp: int) -> str:
    key = base64.b32decode(secret)
    digest = hmac.new(key, struct.pack(">Q", timestamp // 30), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


def probe_concurrent_totp_replay() -> None:
    """Two simultaneous logins with the same TOTP code: at most one may succeed."""
    secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    outcomes = []
    for attempt in range(3):
        user_id, email = create_user(f"rd-mfa-{attempt}")
        with mig() as c:
            c.execute(
                "UPDATE users SET mfa_enabled = TRUE, mfa_secret = %s WHERE id = %s",
                (secret, user_id),
            )
        now = int(time.time())
        if now % 30 > 25:  # avoid a step boundary during the race
            time.sleep(31 - now % 30)
        code = _totp(secret, int(time.time()))
        app = app_for()
        barrier = threading.Barrier(2)
        statuses: list[int] = []
        lock = threading.Lock()

        def worker() -> None:
            with client_for(app) as client:
                barrier.wait()
                status = login(client, email, mfa_code=code).status_code
                with lock:
                    statuses.append(status)

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(30)
        outcomes.append(sorted(statuses))
    results["RD_concurrent_totp_same_code"] = {
        "statuses_per_attempt": outcomes,
        "max_successes_in_any_attempt": max(s.count(200) for s in outcomes),
    }


def probe_limiter_full_table_scan() -> None:
    """Offline: cost of recording a new key when every bounded slot is already blocked."""
    limiter = LoginRateLimiter(limit=10, window_seconds=60)
    max_keys = limiter.max_keys
    for index in range(max_keys):
        key = f"blocked-{index}"
        for _ in range(10):
            limiter.record_failure(key)
    start = time.perf_counter()
    for index in range(200):
        limiter.record_failure(f"new-{index}")
    elapsed_ms = (time.perf_counter() - start) * 1000
    results["RE_limiter_new_key_when_table_full_of_blocked_keys"] = {
        "max_keys": max_keys,
        "new_keys_recorded": sum(1 for k in limiter._windows if k.startswith("new-")),
        "avg_ms_per_new_key": round(elapsed_ms / 200, 3),
    }


if __name__ == "__main__":
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    shared = app_for()
    probe_reset_toctou(shared)
    probe_invitation_toctou(shared)
    probe_ip_limiter_shared_peer()
    probe_concurrent_totp_replay()
    probe_limiter_full_table_scan()
    payload = {"started_at": started, "run": RUN, "results": results}
    OUT.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
