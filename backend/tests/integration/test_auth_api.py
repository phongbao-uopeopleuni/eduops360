"""Live API security tests against an isolated, synthetic PostgreSQL database."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time
from contextlib import closing
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.event_loop import create_event_loop
from app.main import create_app
from app.modules.auth.services import hash_password, hash_session_token

MIGRATOR_DSN = os.getenv("EDUOPS_TEST_MIGRATOR_DSN")
RUNTIME_DSN = os.getenv("EDUOPS_TEST_RUNTIME_DSN")

pytestmark = pytest.mark.skipif(
    not all((MIGRATOR_DSN, RUNTIME_DSN)),
    reason="isolated PostgreSQL auth API DSNs are not configured",
)


def _app_database_url() -> str:
    assert RUNTIME_DSN is not None
    return RUNTIME_DSN.replace("postgresql://", "postgresql+psycopg://", 1)


def _insert_user(connection, *, email: str, password: str, status: str = "active") -> UUID:
    user_id = uuid4()
    connection.execute(
        """
        INSERT INTO users (id, email, password_hash, display_name, status)
        VALUES (%s, %s, %s, 'Synthetic API Test', %s)
        """,
        (user_id, email, hash_password(password), status),
    )
    return user_id


def _insert_role(connection, *, code: str, name: str, permission_codes: tuple[str, ...]) -> UUID:
    role_id = uuid4()
    connection.execute(
        "INSERT INTO roles (id, code, name_vi) VALUES (%s, %s, %s)",
        (role_id, code, name),
    )
    connection.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT %s, id FROM permissions WHERE code = ANY(%s)
        """,
        (role_id, list(permission_codes)),
    )
    return role_id


def _csrf_headers(client: TestClient) -> dict[str, str]:
    token = client.cookies.get("eduops_csrf")
    assert token
    return {"X-CSRF-Token": token}


def _client(app) -> TestClient:
    return TestClient(
        app,
        base_url="https://testserver",
        backend_options={"loop_factory": create_event_loop},
    )


def _totp_code(secret: str, timestamp: int) -> tuple[str, int]:
    step = timestamp // 30
    key = base64.b32decode(secret)
    digest = hmac.new(key, struct.pack(">Q", step), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}", step


def test_login_cookie_csrf_expiry_logout_and_rate_limit() -> None:
    suffix = uuid4().hex
    email = f"login-{suffix}@example.com"
    password = "Synthetic-Password-123!"
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        user_id = _insert_user(migrator, email=email, password=password)

    app = create_app(
        Settings(
            database_url=_app_database_url(),
            environment="test",
            login_rate_limit_attempts=2,
            login_rate_limit_window_seconds=60,
            _env_file=None,
        )
    )
    with _client(app) as client:
        response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200
        assert "access_token" not in response.json()
        cookies = response.headers.get_list("set-cookie")
        session_cookie = next(value for value in cookies if value.startswith("eduops_session="))
        assert "HttpOnly" in session_cookie
        assert "Secure" in session_cookie
        assert "SameSite=strict" in session_cookie

        assert client.get("/api/v1/auth/me").status_code == 200
        assert client.post("/api/v1/auth/logout").status_code == 403
        assert (
            client.post(
                "/api/v1/auth/logout",
                headers={"X-CSRF-Token": "wrong-token"},
            ).status_code
            == 403
        )
        assert client.post("/api/v1/auth/logout", headers=_csrf_headers(client)).status_code == 204
        assert client.get("/api/v1/auth/me").status_code == 401

        unknown = f"unknown-{suffix}@example.com"
        body = {"email": unknown, "password": "wrong-password"}
        assert client.post("/api/v1/auth/login", json=body).status_code == 401
        assert client.post("/api/v1/auth/login", json=body).status_code == 401
        limited = client.post("/api/v1/auth/login", json=body)
        assert limited.status_code == 429
        assert int(limited.headers["Retry-After"]) >= 1

    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        assert migrator.execute(
            "SELECT count(*) FROM sessions WHERE user_id = %s AND status = 'revoked'",
            (user_id,),
        ).fetchone() == (1,)


def test_expired_and_database_revoked_sessions_are_rejected() -> None:
    suffix = uuid4().hex
    email = f"expiry-{suffix}@example.com"
    password = "Synthetic-Password-123!"
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        _insert_user(migrator, email=email, password=password)

    app = create_app(Settings(database_url=_app_database_url(), environment="test", _env_file=None))
    with _client(app) as client:
        assert (
            client.post(
                "/api/v1/auth/login", json={"email": email, "password": password}
            ).status_code
            == 200
        )
        raw_token = client.cookies.get("eduops_session")
        assert raw_token
        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
            migrator.execute(
                "UPDATE sessions SET expires_at = now() - interval '1 minute' "
                "WHERE token_hash = %s",
                (hash_session_token(raw_token),),
            )
        assert client.get("/api/v1/auth/me").status_code == 401

        client.cookies.clear()
        assert (
            client.post(
                "/api/v1/auth/login", json={"email": email, "password": password}
            ).status_code
            == 200
        )
        raw_token = client.cookies.get("eduops_session")
        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
            migrator.execute(
                "UPDATE sessions SET status = 'revoked', revoked_at = now() WHERE token_hash = %s",
                (hash_session_token(raw_token),),
            )
        assert client.get("/api/v1/auth/me").status_code == 401


def test_login_rate_limit_blocks_password_spray_from_one_ip() -> None:
    suffix = uuid4().hex
    app = create_app(
        Settings(
            database_url=_app_database_url(),
            environment="test",
            login_rate_limit_attempts=10,
            login_ip_rate_limit_attempts=2,
            login_rate_limit_window_seconds=60,
            _env_file=None,
        )
    )
    with _client(app) as client:
        statuses = [
            client.post(
                "/api/v1/auth/login",
                json={"email": f"spray-{index}-{suffix}@example.com", "password": "wrong"},
            ).status_code
            for index in range(3)
        ]
    assert statuses == [401, 401, 429]


def test_idle_session_is_expired() -> None:
    suffix = uuid4().hex
    email = f"idle-{suffix}@example.com"
    password = "Synthetic-Password-123!"
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        user_id = _insert_user(migrator, email=email, password=password)

    app = create_app(
        Settings(
            database_url=_app_database_url(),
            environment="test",
            session_idle_timeout_minutes=30,
            _env_file=None,
        )
    )
    with _client(app) as client:
        assert (
            client.post(
                "/api/v1/auth/login", json={"email": email, "password": password}
            ).status_code
            == 200
        )
        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
            migrator.execute(
                "UPDATE sessions SET last_activity_at = now() - interval '31 minutes' "
                "WHERE user_id = %s AND status = 'active'",
                (user_id,),
            )
        assert client.get("/api/v1/auth/me").status_code == 401

    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        assert migrator.execute(
            "SELECT count(*) FROM sessions WHERE user_id = %s AND status = 'expired'",
            (user_id,),
        ).fetchone() == (1,)


def test_totp_step_cannot_be_replayed() -> None:
    suffix = uuid4().hex
    email = f"mfa-replay-{suffix}@example.com"
    password = "Synthetic-Password-123!"
    secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    code, step = _totp_code(secret, int(time.time()))
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        user_id = _insert_user(migrator, email=email, password=password)
        migrator.execute(
            "UPDATE users SET mfa_enabled = TRUE, mfa_secret = %s WHERE id = %s",
            (secret, user_id),
        )

    app = create_app(Settings(database_url=_app_database_url(), environment="test", _env_file=None))
    payload = {"email": email, "password": password, "mfa_code": code}
    with _client(app) as first, _client(app) as replay:
        assert first.post("/api/v1/auth/login", json=payload).status_code == 200
        assert replay.post("/api/v1/auth/login", json=payload).status_code == 401

    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        assert migrator.execute(
            "SELECT mfa_last_used_step FROM users WHERE id = %s", (user_id,)
        ).fetchone() == (step,)


def test_pending_invitation_can_be_reissued_cancelled_and_privilege_bounded() -> None:
    suffix = uuid4().hex
    admin_email = f"invite-admin-{suffix}@example.com"
    password = "Synthetic-Password-123!"
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        admin_id = _insert_user(migrator, email=admin_email, password=password)
        admin_role_id = _insert_role(
            migrator,
            code=f"test_invite_{suffix[:12]}",
            name="Synthetic Invitation Admin",
            permission_codes=("user:create", "user:suspend"),
        )
        migrator.execute(
            "INSERT INTO user_roles (id, user_id, role_id) VALUES (%s, %s, %s)",
            (uuid4(), admin_id, admin_role_id),
        )

    app = create_app(Settings(database_url=_app_database_url(), environment="test", _env_file=None))
    with _client(app) as admin:
        assert (
            admin.post(
                "/api/v1/auth/login", json={"email": admin_email, "password": password}
            ).status_code
            == 200
        )

        first = admin.post(
            "/api/v1/admin/users/invitations",
            json={"email": f"reissue-{suffix}@example.com", "display_name": "Reissue"},
            headers=_csrf_headers(admin),
        ).json()
        reissued = admin.post(
            f"/api/v1/admin/users/{first['user']['id']}/invitation",
            json={"valid_hours": 48},
            headers=_csrf_headers(admin),
        )
        assert reissued.status_code == 201
        second_token = reissued.json()["one_time_token"]
        assert second_token != first["one_time_token"]
        assert (
            admin.post(
                "/api/v1/auth/invitations/accept",
                json={"token": first["one_time_token"], "password": password},
            ).status_code
            == 400
        )
        assert (
            admin.post(
                "/api/v1/auth/invitations/accept",
                json={"token": second_token, "password": password},
            ).status_code
            == 204
        )

        cancelled = admin.post(
            "/api/v1/admin/users/invitations",
            json={"email": f"cancel-{suffix}@example.com", "display_name": "Cancel"},
            headers=_csrf_headers(admin),
        ).json()
        assert (
            admin.post(
                f"/api/v1/admin/users/{cancelled['user']['id']}/invitation/cancel",
                headers=_csrf_headers(admin),
            ).status_code
            == 204
        )
        assert (
            admin.post(
                "/api/v1/auth/invitations/accept",
                json={"token": cancelled["one_time_token"], "password": password},
            ).status_code
            == 400
        )

        bounded = admin.post(
            "/api/v1/admin/users/invitations",
            json={"email": f"bounded-{suffix}@example.com", "display_name": "Bounded"},
            headers=_csrf_headers(admin),
        ).json()
        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
            privileged_role = _insert_role(
                migrator,
                code=f"test_privileged_{suffix[:12]}",
                name="Synthetic Privileged Invitee",
                permission_codes=("audit:read",),
            )
            migrator.execute(
                "INSERT INTO user_roles (id, user_id, role_id) VALUES (%s, %s, %s)",
                (uuid4(), bounded["user"]["id"], privileged_role),
            )
        denied = admin.post(
            f"/api/v1/admin/users/{bounded['user']['id']}/invitation",
            json={},
            headers=_csrf_headers(admin),
        )
        assert denied.status_code == 403
        assert denied.json()["error"]["code"] == "TARGET_PRIVILEGE_EXCEEDS_ACTOR"

    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        actions = dict(
            migrator.execute(
                "SELECT action, count(*) FROM audit_logs "
                "WHERE action IN ('user:invitation_reissue', 'user:invitation_cancel') "
                "AND actor_id = %s GROUP BY action",
                (admin_id,),
            ).fetchall()
        )
        assert actions == {"user:invitation_cancel": 1, "user:invitation_reissue": 1}


def test_admin_guards_deny_csrf_idor_escalation_and_stale_grants() -> None:
    suffix = uuid4().hex
    admin_email = f"admin-{suffix}@example.com"
    scoped_email = f"scoped-{suffix}@example.com"
    password = "Synthetic-Password-123!"
    school_id = uuid4()
    year_id = uuid4()

    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        admin_id = _insert_user(migrator, email=admin_email, password=password)
        scoped_id = _insert_user(migrator, email=scoped_email, password=password)
        permission_codes = (
            "user:create",
            "user:read",
            "user:suspend",
            "user:activate",
            "user:grant_role",
            "user:revoke_role",
            "audit:read",
        )
        admin_role_id = _insert_role(
            migrator,
            code=f"test_admin_{suffix}",
            name="Synthetic Test Admin",
            permission_codes=permission_codes,
        )
        auditor_role_id = _insert_role(
            migrator,
            code=f"test_audit_{suffix}",
            name="Synthetic Test Auditor",
            permission_codes=("audit:read",),
        )
        scoped_role_id = _insert_role(
            migrator,
            code=f"test_scoped_{suffix}",
            name="Synthetic Scoped Admin",
            permission_codes=("user:read", "user:grant_role", "user:revoke_role"),
        )
        admin_grant_id = uuid4()
        scoped_grant_id = uuid4()
        migrator.execute(
            """
            INSERT INTO user_roles (id, user_id, role_id)
            VALUES (%s, %s, %s)
            """,
            (admin_grant_id, admin_id, admin_role_id),
        )
        migrator.execute(
            """
            INSERT INTO user_roles (
                id, user_id, role_id, school_id, academic_year_id
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (scoped_grant_id, scoped_id, scoped_role_id, school_id, year_id),
        )

    app = create_app(Settings(database_url=_app_database_url(), environment="test", _env_file=None))
    with _client(app) as admin_client:
        assert (
            admin_client.post(
                "/api/v1/auth/login",
                json={"email": admin_email, "password": password},
            ).status_code
            == 200
        )
        create_payload = {
            "email": f"created-{suffix}@example.com",
            "display_name": "Created User",
        }
        assert (
            admin_client.post(
                "/api/v1/admin/users/invitations",
                json=create_payload,
            ).status_code
            == 403
        )
        created = admin_client.post(
            "/api/v1/admin/users/invitations",
            json=create_payload,
            headers=_csrf_headers(admin_client),
        )
        assert created.status_code == 201
        target_user_id = created.json()["user"]["id"]

    with _client(app) as scoped_client:
        assert (
            scoped_client.post(
                "/api/v1/auth/login",
                json={"email": scoped_email, "password": password},
            ).status_code
            == 200
        )
        assert scoped_client.get(f"/api/v1/admin/users/{target_user_id}").status_code == 403
        escalation = scoped_client.post(
            f"/api/v1/admin/users/{target_user_id}/roles",
            json={
                "role_id": str(auditor_role_id),
                "school_id": str(school_id),
                "academic_year_id": str(year_id),
            },
            headers=_csrf_headers(scoped_client),
        )
        assert escalation.status_code == 403
        assert escalation.json()["error"]["code"] == "ROLE_ESCALATION_DENIED"

        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
            migrator.execute(
                "UPDATE user_roles SET is_active = FALSE, revoked_at = now() WHERE id = %s",
                (scoped_grant_id,),
            )
        stale = scoped_client.post(
            f"/api/v1/admin/users/{target_user_id}/roles",
            json={
                "role_id": str(auditor_role_id),
                "school_id": str(school_id),
                "academic_year_id": str(year_id),
            },
            headers=_csrf_headers(scoped_client),
        )
        assert stale.status_code == 403


def test_invitation_and_password_reset_tokens_are_single_use_and_revoke_sessions() -> None:
    suffix = uuid4().hex
    admin_email = f"token-admin-{suffix}@example.com"
    invited_email = f"invited-{suffix}@example.com"
    expired_email = f"expired-invite-{suffix}@example.com"
    admin_password = "Synthetic-Admin-Password-123!"
    initial_password = "Synthetic-Invited-Password-123!"
    replacement_password = "Synthetic-Replacement-Password-456!"

    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        admin_id = _insert_user(
            migrator,
            email=admin_email,
            password=admin_password,
        )
        admin_role_id = _insert_role(
            migrator,
            code=f"test_token_admin_{suffix}",
            name="Synthetic Token Admin",
            permission_codes=("user:create", "user:password_reset"),
        )
        migrator.execute(
            "INSERT INTO user_roles (id, user_id, role_id) VALUES (%s, %s, %s)",
            (uuid4(), admin_id, admin_role_id),
        )

    app = create_app(Settings(database_url=_app_database_url(), environment="test", _env_file=None))
    with _client(app) as admin_client:
        assert (
            admin_client.post(
                "/api/v1/auth/login",
                json={"email": admin_email, "password": admin_password},
            ).status_code
            == 200
        )
        invitation = admin_client.post(
            "/api/v1/admin/users/invitations",
            json={"email": invited_email, "display_name": "Invited User"},
            headers=_csrf_headers(admin_client),
        )
        assert invitation.status_code == 201
        invitation_body = invitation.json()
        invited_user_id = invitation_body["user"]["id"]
        invitation_token = invitation_body["one_time_token"]

        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
            stored_hash = migrator.execute(
                "SELECT token_hash FROM account_tokens WHERE user_id = %s",
                (invited_user_id,),
            ).fetchone()[0]
            assert stored_hash == hash_session_token(invitation_token)
            assert stored_hash != invitation_token

        accepted = admin_client.post(
            "/api/v1/auth/invitations/accept",
            json={"token": invitation_token, "password": initial_password},
        )
        assert accepted.status_code == 204
        assert (
            admin_client.post(
                "/api/v1/auth/invitations/accept",
                json={"token": invitation_token, "password": initial_password},
            ).status_code
            == 400
        )

        expired_invitation = admin_client.post(
            "/api/v1/admin/users/invitations",
            json={"email": expired_email, "display_name": "Expired Invite"},
            headers=_csrf_headers(admin_client),
        )
        assert expired_invitation.status_code == 201
        expired_body = expired_invitation.json()
        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
            migrator.execute(
                "UPDATE account_tokens SET expires_at = now() - interval '1 minute' "
                "WHERE user_id = %s",
                (expired_body["user"]["id"],),
            )
        assert (
            admin_client.post(
                "/api/v1/auth/invitations/accept",
                json={
                    "token": expired_body["one_time_token"],
                    "password": initial_password,
                },
            ).status_code
            == 400
        )

        reset = admin_client.post(
            f"/api/v1/admin/users/{invited_user_id}/password-reset",
            json={},
            headers=_csrf_headers(admin_client),
        )
        assert reset.status_code == 201
        reset_token = reset.json()["one_time_token"]

    with _client(app) as invited_client:
        assert (
            invited_client.post(
                "/api/v1/auth/login",
                json={"email": invited_email, "password": initial_password},
            ).status_code
            == 200
        )
        assert invited_client.get("/api/v1/auth/me").status_code == 200
        assert (
            invited_client.post(
                "/api/v1/auth/password-reset/accept",
                json={"token": reset_token, "new_password": replacement_password},
            ).status_code
            == 204
        )
        assert invited_client.get("/api/v1/auth/me").status_code == 401
        assert (
            invited_client.post(
                "/api/v1/auth/password-reset/accept",
                json={"token": reset_token, "new_password": replacement_password},
            ).status_code
            == 400
        )
        invited_client.cookies.clear()
        assert (
            invited_client.post(
                "/api/v1/auth/login",
                json={"email": invited_email, "password": initial_password},
            ).status_code
            == 401
        )
        assert (
            invited_client.post(
                "/api/v1/auth/login",
                json={"email": invited_email, "password": replacement_password},
            ).status_code
            == 200
        )

    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as migrator:
        assert migrator.execute(
            """
            SELECT count(*) FROM audit_logs
            WHERE concat_ws(
                ' ', before_state::text, after_state::text, extra_data::text, reason
            ) LIKE %s
            """,
            (f"%{invitation_token}%",),
        ).fetchone() == (0,)
        assert migrator.execute(
            "SELECT count(*) FROM account_tokens WHERE used_at IS NOT NULL AND user_id = %s",
            (invited_user_id,),
        ).fetchone() == (2,)
