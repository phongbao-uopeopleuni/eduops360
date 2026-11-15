"""Live PostgreSQL regressions for EDU-0032 (audit findings A0102-F01..F06, F08).

Skipped unless isolated synthetic DSNs are configured. Each test creates its own
synthetic roles instead of changing the global (intentionally unseeded) role mappings.
"""

from __future__ import annotations

import asyncio
import os
from contextlib import closing
from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import func, update

from app.core.config import Settings
from app.core.errors import AppError
from app.core.event_loop import create_event_loop
from app.db.connection import Database
from app.main import create_app
from app.modules.auth.models import AccountToken
from app.modules.auth.rate_limit import LoginRateLimiter
from app.modules.auth.router import _consume_account_token
from app.modules.auth.services import generate_session_token, hash_password, hash_session_token

MIGRATOR_DSN = os.getenv("EDUOPS_TEST_MIGRATOR_DSN")
RUNTIME_DSN = os.getenv("EDUOPS_TEST_RUNTIME_DSN")

pytestmark = pytest.mark.skipif(
    not all((MIGRATOR_DSN, RUNTIME_DSN)),
    reason="isolated PostgreSQL auth API DSNs are not configured",
)

PASSWORD = "Synthetic-Password-123!"
LONG_USER_AGENT = "Mozilla/5.0 " + "A" * 600
FULL_USER_ADMIN = [
    "user:create",
    "user:read",
    "user:suspend",
    "user:activate",
    "user:password_reset",
    "user:grant_role",
    "user:revoke_role",
]


def _runtime_sqlalchemy_url() -> str:
    assert RUNTIME_DSN is not None
    return RUNTIME_DSN.replace("postgresql://", "postgresql+psycopg://", 1)


def _migrator():
    return closing(psycopg.connect(MIGRATOR_DSN, autocommit=True))


def _user(label: str, *, status: str = "active") -> tuple[UUID, str]:
    user_id = uuid4()
    email = f"{label}-{uuid4().hex[:12]}@example.com"
    with _migrator() as connection:
        connection.execute(
            "INSERT INTO users (id, email, password_hash, display_name, status) "
            "VALUES (%s, %s, %s, 'Synthetic Remediation Test', %s)",
            (user_id, email, hash_password(PASSWORD), status),
        )
    return user_id, email


def _role(label: str, permission_codes: list[str]) -> UUID:
    role_id = uuid4()
    with _migrator() as connection:
        connection.execute(
            "INSERT INTO roles (id, code, name_vi) VALUES (%s, %s, 'Synthetic remediation role')",
            (role_id, f"edu0032_{label}_{uuid4().hex[:10]}"),
        )
        inserted = connection.execute(
            "INSERT INTO role_permissions (role_id, permission_id) "
            "SELECT %s, id FROM permissions WHERE code = ANY(%s)",
            (role_id, permission_codes),
        ).rowcount
    assert inserted == len(permission_codes)
    return role_id


def _grant(user_id: UUID, role_id: UUID, *, school=None, year=None, grade=None) -> UUID:
    grant_id = uuid4()
    with _migrator() as connection:
        connection.execute(
            "INSERT INTO user_roles "
            "(id, user_id, role_id, school_id, academic_year_id, grade_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (grant_id, user_id, role_id, school, year, grade),
        )
    return grant_id


def _app(**overrides):
    return create_app(
        Settings(
            database_url=_runtime_sqlalchemy_url(),
            environment="test",
            _env_file=None,
            **overrides,
        )
    )


def _client(app) -> TestClient:
    return TestClient(
        app,
        base_url="https://testserver",
        backend_options={"loop_factory": create_event_loop},
        raise_server_exceptions=False,
    )


def _csrf(client: TestClient) -> dict[str, str]:
    token = client.cookies.get("eduops_csrf")
    assert token
    return {"X-CSRF-Token": token}


def _login(client: TestClient, email: str, password: str = PASSWORD, *, user_agent=None):
    headers = {"User-Agent": user_agent} if user_agent else {}
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
        headers=headers,
    )


def _error_code(response) -> str | None:
    return response.json().get("error", {}).get("code")


def _user_row(user_id: UUID) -> tuple[str, int, datetime | None]:
    with _migrator() as connection:
        return connection.execute(
            "SELECT status, failed_login_count, locked_until FROM users WHERE id = %s",
            (user_id,),
        ).fetchone()


def test_f01_reset_and_status_change_require_actor_to_cover_target_privileges() -> None:
    full = _role("full", FULL_USER_ADMIN)
    reset_only = _role("reset_only", ["user:password_reset"])
    suspend_only = _role("suspend_only", ["user:suspend"])
    activate_only = _role("activate_only", ["user:activate"])
    superior_id, _ = _user("f01-superior")
    _grant(superior_id, full)
    suspended_superior_id, _ = _user("f01-suspended-superior", status="suspended")
    _grant(suspended_superior_id, full)
    peer_admin_id, peer_admin_email = _user("f01-peer-admin")
    _grant(peer_admin_id, full)
    resetter_id, resetter_email = _user("f01-reset-only")
    _grant(resetter_id, reset_only)
    suspender_id, suspender_email = _user("f01-suspend-only")
    _grant(suspender_id, suspend_only)
    activator_id, activator_email = _user("f01-activate-only")
    _grant(activator_id, activate_only)
    plain_id, plain_email = _user("f01-plain")

    app = _app()
    with _client(app) as resetter:
        assert _login(resetter, resetter_email).status_code == 200
        denied = resetter.post(
            f"/api/v1/admin/users/{superior_id}/password-reset",
            json={},
            headers=_csrf(resetter),
        )
        assert denied.status_code == 403
        assert _error_code(denied) == "TARGET_PRIVILEGE_EXCEEDS_ACTOR"

        allowed = resetter.post(
            f"/api/v1/admin/users/{plain_id}/password-reset",
            json={},
            headers=_csrf(resetter),
        )
        assert allowed.status_code == 201
        reset_token = allowed.json()["one_time_token"]
        assert (
            resetter.post(
                "/api/v1/auth/password-reset/accept",
                json={"token": reset_token, "new_password": "Synthetic-Replaced-Pass-1!"},
            ).status_code
            == 204
        )

    with _client(app) as suspender:
        assert _login(suspender, suspender_email).status_code == 200
        denied = suspender.patch(
            f"/api/v1/admin/users/{superior_id}/status",
            json={"status": "suspended", "reason": "synthetic regression"},
            headers=_csrf(suspender),
        )
        assert denied.status_code == 403
        assert _error_code(denied) == "TARGET_PRIVILEGE_EXCEEDS_ACTOR"
        assert (
            suspender.patch(
                f"/api/v1/admin/users/{plain_id}/status",
                json={"status": "suspended", "reason": "synthetic regression"},
                headers=_csrf(suspender),
            ).status_code
            == 200
        )

    with _client(app) as activator:
        assert _login(activator, activator_email).status_code == 200
        denied = activator.patch(
            f"/api/v1/admin/users/{suspended_superior_id}/status",
            json={"status": "active", "reason": "synthetic regression"},
            headers=_csrf(activator),
        )
        assert denied.status_code == 403
        assert _error_code(denied) == "TARGET_PRIVILEGE_EXCEEDS_ACTOR"

    with _client(app) as peer_admin:
        assert _login(peer_admin, peer_admin_email).status_code == 200
        assert (
            peer_admin.post(
                f"/api/v1/admin/users/{superior_id}/password-reset",
                json={},
                headers=_csrf(peer_admin),
            ).status_code
            == 201
        )

    assert _user_row(superior_id)[0] == "active"
    assert _user_row(suspended_superior_id)[0] == "suspended"
    with _migrator() as connection:
        accept_extra = connection.execute(
            "SELECT actor_id, extra_data FROM audit_logs "
            "WHERE action = 'user:password_reset_accept' AND resource_id = %s",
            (str(plain_id),),
        ).fetchone()
        superior_tokens_by_resetter = connection.execute(
            "SELECT count(*) FROM account_tokens WHERE user_id = %s AND created_by = %s",
            (superior_id, resetter_id),
        ).fetchone()[0]
    assert accept_extra is not None
    assert accept_extra[0] == plain_id
    assert accept_extra[1]["issued_by"] == str(resetter_id)
    assert superior_tokens_by_resetter == 0
    assert plain_email


def test_r42_f01_reset_token_rechecks_issuer_permission_and_target_coverage() -> None:
    full = _role("r42_reset_full", FULL_USER_ADMIN)
    reset_only = _role("r42_reset_only", ["user:password_reset"])
    scoped = _role("r42_reset_scoped", ["user:read"])
    school_id, year_id = uuid4(), uuid4()

    resetter_id, resetter_email = _user("r42-resetter")
    resetter_grant = _grant(resetter_id, reset_only)
    promoted_id, promoted_email = _user("r42-reset-promoted")
    revoked_target_id, _ = _user("r42-reset-revoked-issuer")

    full_admin_id, full_admin_email = _user("r42-reset-full-admin")
    _grant(full_admin_id, full)
    covered_id, covered_email = _user("r42-reset-covered")

    app = _app()
    with _client(app) as resetter:
        assert _login(resetter, resetter_email).status_code == 200
        promoted_token = resetter.post(
            f"/api/v1/admin/users/{promoted_id}/password-reset",
            json={},
            headers=_csrf(resetter),
        ).json()["one_time_token"]
        revoked_issuer_token = resetter.post(
            f"/api/v1/admin/users/{revoked_target_id}/password-reset",
            json={},
            headers=_csrf(resetter),
        ).json()["one_time_token"]

    _grant(promoted_id, scoped, school=school_id, year=year_id)
    with _migrator() as connection:
        connection.execute(
            "UPDATE user_roles SET is_active = FALSE, revoked_at = now() WHERE id = %s",
            (resetter_grant,),
        )

    with _client(app) as anonymous:
        promoted = anonymous.post(
            "/api/v1/auth/password-reset/accept",
            json={"token": promoted_token, "new_password": "R42-Promoted-Takeover-1!"},
        )
        assert promoted.status_code == 400
        assert _error_code(promoted) == "ACCOUNT_TOKEN_INVALID"
        revoked = anonymous.post(
            "/api/v1/auth/password-reset/accept",
            json={"token": revoked_issuer_token, "new_password": "R42-Revoked-Issuer-1!"},
        )
        assert revoked.status_code == 400
        assert _error_code(revoked) == "ACCOUNT_TOKEN_INVALID"

    with _client(app) as promoted_login:
        assert _login(promoted_login, promoted_email).status_code == 200
        promoted_login.cookies.clear()
        assert _login(promoted_login, promoted_email, "R42-Promoted-Takeover-1!").status_code == 401

    with _client(app) as full_admin:
        assert _login(full_admin, full_admin_email).status_code == 200
        covered_token = full_admin.post(
            f"/api/v1/admin/users/{covered_id}/password-reset",
            json={},
            headers=_csrf(full_admin),
        ).json()["one_time_token"]
    _grant(covered_id, scoped, school=school_id, year=year_id)
    with _client(app) as anonymous:
        assert (
            anonymous.post(
                "/api/v1/auth/password-reset/accept",
                json={"token": covered_token, "new_password": "R42-Covered-Reset-1!"},
            ).status_code
            == 204
        )
    with _client(app) as covered_login:
        assert _login(covered_login, covered_email, "R42-Covered-Reset-1!").status_code == 200


def test_r42_f01_invitation_rechecks_issuer_permission_and_target_coverage() -> None:
    full = _role("r42_invite_full", FULL_USER_ADMIN)
    create_only = _role("r42_invite_only", ["user:create"])
    scoped = _role("r42_invite_scoped", ["user:read"])
    school_id, year_id = uuid4(), uuid4()

    inviter_id, inviter_email = _user("r42-inviter")
    _grant(inviter_id, create_only)
    full_admin_id, full_admin_email = _user("r42-invite-full-admin")
    _grant(full_admin_id, full)
    app = _app()

    denied_email = f"r42-invite-denied-{uuid4().hex[:12]}@example.com"
    with _client(app) as inviter:
        assert _login(inviter, inviter_email).status_code == 200
        invitation = inviter.post(
            "/api/v1/admin/users/invitations",
            json={"email": denied_email, "display_name": "R42 Denied Invitee"},
            headers=_csrf(inviter),
        )
        assert invitation.status_code == 201
        denied_id = UUID(invitation.json()["user"]["id"])
        denied_token = invitation.json()["one_time_token"]
    _grant(denied_id, scoped, school=school_id, year=year_id)

    with _client(app) as anonymous:
        denied = anonymous.post(
            "/api/v1/auth/invitations/accept",
            json={"token": denied_token, "password": "R42-Invitation-Takeover-1!"},
        )
        assert denied.status_code == 400
        assert _error_code(denied) == "ACCOUNT_TOKEN_INVALID"
    assert _user_row(denied_id)[0] == "pending"

    covered_email = f"r42-invite-covered-{uuid4().hex[:12]}@example.com"
    with _client(app) as full_admin:
        assert _login(full_admin, full_admin_email).status_code == 200
        invitation = full_admin.post(
            "/api/v1/admin/users/invitations",
            json={"email": covered_email, "display_name": "R42 Covered Invitee"},
            headers=_csrf(full_admin),
        )
        assert invitation.status_code == 201
        covered_id = UUID(invitation.json()["user"]["id"])
        covered_token = invitation.json()["one_time_token"]
    _grant(covered_id, scoped, school=school_id, year=year_id)

    with _client(app) as anonymous:
        assert (
            anonymous.post(
                "/api/v1/auth/invitations/accept",
                json={"token": covered_token, "password": "R42-Covered-Invitation-1!"},
            ).status_code
            == 204
        )
    with _client(app) as covered_login:
        assert _login(covered_login, covered_email, "R42-Covered-Invitation-1!").status_code == 200


def test_f02_long_user_agent_still_locks_account_and_audits_failures() -> None:
    victim_id, victim_email = _user("f02-victim")
    survivor_id, survivor_email = _user("f02-survivor")
    app = _app()
    with _client(app) as client:
        statuses = [
            _login(client, victim_email, "wrong-password", user_agent=LONG_USER_AGENT).status_code
            for _ in range(5)
        ]
        assert statuses == [401] * 5
        assert _login(client, victim_email, user_agent=LONG_USER_AGENT).status_code == 401

    with _client(app) as client:
        success = _login(client, survivor_email, user_agent=LONG_USER_AGENT)
        assert success.status_code == 200

    status, failed_count, locked_until = _user_row(victim_id)
    assert (status, failed_count) == ("locked", 5)
    assert locked_until is not None
    with _migrator() as connection:
        failed_audits = connection.execute(
            "SELECT char_length(user_agent) FROM audit_logs "
            "WHERE actor_id = %s AND action = 'session:login_failed'",
            (victim_id,),
        ).fetchall()
        session_agent = connection.execute(
            "SELECT char_length(user_agent) FROM sessions WHERE user_id = %s",
            (survivor_id,),
        ).fetchone()
    assert len(failed_audits) == 6
    assert {row[0] for row in failed_audits} == {500}
    assert session_agent == (500,)


def test_f03_pending_account_status_cannot_bypass_invitation() -> None:
    full = _role("f03_full", FULL_USER_ADMIN)
    admin_id, admin_email = _user("f03-admin")
    _grant(admin_id, full)
    invitee_email = f"f03-invitee-{uuid4().hex[:12]}@example.com"
    invitee_password = "Synthetic-Invitee-Pass-1!"
    app = _app()
    with _client(app) as admin:
        assert _login(admin, admin_email).status_code == 200
        invitation = admin.post(
            "/api/v1/admin/users/invitations",
            json={"email": invitee_email, "display_name": "Synthetic Invitee"},
            headers=_csrf(admin),
        )
        assert invitation.status_code == 201
        target_id = invitation.json()["user"]["id"]
        invitation_token = invitation.json()["one_time_token"]

        for requested in ("active", "suspended"):
            denied = admin.patch(
                f"/api/v1/admin/users/{target_id}/status",
                json={"status": requested, "reason": "synthetic regression"},
                headers=_csrf(admin),
            )
            assert denied.status_code == 409
            assert _error_code(denied) == "INVITATION_REQUIRED"
        assert _user_row(UUID(target_id))[0] == "pending"

        assert (
            admin.post(
                "/api/v1/auth/invitations/accept",
                json={"token": invitation_token, "password": invitee_password},
            ).status_code
            == 204
        )
        assert _user_row(UUID(target_id))[0] == "active"

        repeated = admin.patch(
            f"/api/v1/admin/users/{target_id}/status",
            json={"status": "active", "reason": "synthetic regression"},
            headers=_csrf(admin),
        )
        assert repeated.status_code == 409
        assert _error_code(repeated) == "INVALID_STATUS_TRANSITION"
        assert (
            admin.patch(
                f"/api/v1/admin/users/{target_id}/status",
                json={"status": "suspended", "reason": "synthetic regression"},
                headers=_csrf(admin),
            ).status_code
            == 200
        )
        assert (
            admin.patch(
                f"/api/v1/admin/users/{target_id}/status",
                json={"status": "active", "reason": "synthetic regression"},
                headers=_csrf(admin),
            ).status_code
            == 200
        )

    with _client(app) as invitee:
        assert _login(invitee, invitee_email, invitee_password).status_code == 200


async def _race_reset_token(raw_token: str) -> dict:
    database = Database(SecretStr(_runtime_sqlalchemy_url()))
    assert database.session_factory is not None
    limiter = LoginRateLimiter(limit=50, window_seconds=60)
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(login_rate_limiter=limiter)),
        client=SimpleNamespace(host="198.51.100.32"),
    )
    outcome: dict = {}
    try:
        async with (
            database.session_factory() as session_a,
            database.session_factory() as session_b,
        ):
            token_a, _ = await _consume_account_token(
                db=session_a, raw_token=raw_token, purpose="password_reset", request=request
            )
            await session_a.execute(
                update(AccountToken).where(AccountToken.id == token_a.id).values(used_at=func.now())
            )
            await session_a.flush()

            async def second_request() -> str:
                try:
                    await _consume_account_token(
                        db=session_b,
                        raw_token=raw_token,
                        purpose="password_reset",
                        request=request,
                    )
                except AppError as error:
                    return error.code
                return "accepted"

            task = asyncio.create_task(second_request())
            await asyncio.sleep(1.0)
            outcome["second_blocked_until_first_commits"] = not task.done()
            await session_a.commit()
            outcome["second_result"] = await asyncio.wait_for(task, 15)
            await session_b.rollback()
    finally:
        await database.close()
    return outcome


def test_f04_concurrent_reset_token_consumption_is_single_use() -> None:
    user_id, _ = _user("f04-target")
    issuer_id, _ = _user("f04-issuer")
    _grant(issuer_id, _role("f04_issuer", FULL_USER_ADMIN))
    raw_token = generate_session_token()
    with _migrator() as connection:
        connection.execute(
            "INSERT INTO account_tokens "
            "(id, user_id, purpose, token_hash, expires_at, created_by) "
            "VALUES (%s, %s, 'password_reset', %s, now() + interval '1 hour', %s)",
            (uuid4(), user_id, hash_session_token(raw_token), issuer_id),
        )
    outcome = asyncio.run(_race_reset_token(raw_token), loop_factory=create_event_loop)
    assert outcome["second_blocked_until_first_commits"] is True
    assert outcome["second_result"] == "ACCOUNT_TOKEN_INVALID"


def test_f05_failed_login_lockout_keeps_existing_session_but_blocks_new_login() -> None:
    victim_id, victim_email = _user("f05-victim")
    app = _app()
    with _client(app) as victim, _client(app) as attacker:
        assert _login(victim, victim_email).status_code == 200
        assert victim.get("/api/v1/auth/me").status_code == 200
        assert [_login(attacker, victim_email, "wrong-password").status_code for _ in range(5)] == [
            401
        ] * 5
        assert _user_row(victim_id)[0] == "locked"

        still_signed_in = victim.get("/api/v1/auth/me")
        assert still_signed_in.status_code == 200
        assert still_signed_in.json()["id"] == str(victim_id)
        assert victim.post("/api/v1/auth/logout", headers=_csrf(victim)).status_code == 204

    with _client(app) as fresh:
        assert _login(fresh, victim_email).status_code == 401


def test_f06_delegation_denies_self_grant_caps_validity_and_audits_full_scope() -> None:
    school_id, year_id = uuid4(), uuid4()
    scoped = _role("f06_scoped", ["user:read", "user:grant_role", "user:revoke_role"])
    delegator_id, delegator_email = _user("f06-delegator")
    original_grant = _grant(delegator_id, scoped, school=school_id, year=year_id)
    with _migrator() as connection:
        delegator_expiry = connection.execute(
            "UPDATE user_roles SET valid_until = now() + interval '10 minutes' "
            "WHERE id = %s RETURNING valid_until",
            (original_grant,),
        ).fetchone()[0]
    first_id, _ = _user("f06-first")
    second_id, _ = _user("f06-second")
    later_id, _ = _user("f06-later")
    base = {
        "role_id": str(scoped),
        "school_id": str(school_id),
        "academic_year_id": str(year_id),
    }
    app = _app()
    with _client(app) as delegator:
        assert _login(delegator, delegator_email).status_code == 200
        self_grant = delegator.post(
            f"/api/v1/admin/users/{delegator_id}/roles",
            json={**base, "grade_id": 1},
            headers=_csrf(delegator),
        )
        assert self_grant.status_code == 403
        assert _error_code(self_grant) == "SELF_GRANT_DENIED"

        defaulted = delegator.post(
            f"/api/v1/admin/users/{first_id}/roles",
            json=base,
            headers=_csrf(delegator),
        )
        assert defaulted.status_code == 201
        assert datetime.fromisoformat(defaulted.json()["valid_until"]) == delegator_expiry

        too_long = delegator.post(
            f"/api/v1/admin/users/{second_id}/roles",
            json={**base, "valid_until": (delegator_expiry + timedelta(days=1)).isoformat()},
            headers=_csrf(delegator),
        )
        assert too_long.status_code == 422
        assert _error_code(too_long) == "ROLE_VALIDITY_EXCEEDS_DELEGATOR"

        bounded_until = delegator_expiry - timedelta(minutes=5)
        bounded = delegator.post(
            f"/api/v1/admin/users/{second_id}/roles",
            json={**base, "grade_id": 1, "valid_until": bounded_until.isoformat()},
            headers=_csrf(delegator),
        )
        assert bounded.status_code == 201
        bounded_id = bounded.json()["id"]

        with _migrator() as connection:
            connection.execute(
                "UPDATE user_roles SET valid_until = now() - interval '1 minute' WHERE id = %s",
                (original_grant,),
            )
        assert (
            delegator.post(
                f"/api/v1/admin/users/{later_id}/roles",
                json={**base, "grade_id": 1},
                headers=_csrf(delegator),
            ).status_code
            == 403
        )

    with _migrator() as connection:
        after_state = connection.execute(
            "SELECT after_state FROM audit_logs "
            "WHERE action = 'user:grant_role' AND resource_id = %s",
            (bounded_id,),
        ).fetchone()[0]
        self_grants = connection.execute(
            "SELECT count(*) FROM user_roles WHERE user_id = %s",
            (delegator_id,),
        ).fetchone()[0]
    assert {
        "user_id",
        "role_id",
        "school_id",
        "academic_year_id",
        "grade_id",
        "class_id",
        "subject_id",
        "valid_from",
        "valid_until",
    } <= set(after_state)
    assert after_state["grade_id"] == 1
    assert after_state["school_id"] == str(school_id)
    assert datetime.fromisoformat(after_state["valid_until"]) == bounded_until
    assert self_grants == 1


def test_f08_router_lockout_blocks_until_expiry_then_resets() -> None:
    user_id, email = _user("f08-locked")
    with _migrator() as connection:
        connection.execute(
            "UPDATE users SET status = 'locked', failed_login_count = 5, "
            "locked_until = now() + interval '10 minutes' WHERE id = %s",
            (user_id,),
        )
    app = _app()
    with _client(app) as client:
        assert _login(client, email).status_code == 401
        assert _user_row(user_id)[0] == "locked"
        with _migrator() as connection:
            connection.execute(
                "UPDATE users SET locked_until = now() - interval '1 minute' WHERE id = %s",
                (user_id,),
            )
        assert _login(client, email).status_code == 200
    assert _user_row(user_id) == ("active", 0, None)
