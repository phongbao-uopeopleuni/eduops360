"""Live probes against the isolated audit PostgreSQL (compose project eduops360-audit-p0102).

Run from backend/ after sourcing ../.local/audit-phase-01-02/dsn.sh:
    PYTHONPATH=. .venv/Scripts/python.exe -B ../.local/audit-phase-01-02/probe_live.py

Synthetic identities only. Does not modify source code. Writes probe_live.json.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from contextlib import closing
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import psycopg
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

MIGRATOR_DSN = os.environ["EDUOPS_TEST_MIGRATOR_DSN"]
RUNTIME_SQLA = os.environ["EDUOPS_TEST_RUNTIME_DSN"].replace(
    "postgresql://", "postgresql+psycopg://", 1
)
RUN = uuid4().hex[:10]
PASSWORD = "Synthetic-Password-123!"
OUT = Path(__file__).with_name("probe_live.json")
results: dict[str, dict] = {}

FULL = [
    "user:create", "user:read", "user:suspend", "user:activate",
    "user:password_reset", "user:grant_role", "user:revoke_role",
]


def mig():
    return closing(psycopg.connect(MIGRATOR_DSN, autocommit=True))


def create_user(label: str, *, status: str = "active") -> tuple[UUID, str]:
    user_id = uuid4()
    email = f"{label}-{RUN}@example.com"
    with mig() as c:
        c.execute(
            "INSERT INTO users (id, email, password_hash, display_name, status) "
            "VALUES (%s, %s, %s, 'Synthetic Audit Probe', %s)",
            (user_id, email, hash_password(PASSWORD), status),
        )
    return user_id, email


def create_role(label: str, permission_codes: list[str]) -> UUID:
    role_id = uuid4()
    with mig() as c:
        c.execute(
            "INSERT INTO roles (id, code, name_vi) VALUES (%s, %s, 'Synthetic probe role')",
            (role_id, f"audit_probe_{label}_{RUN}"),
        )
        c.execute(
            "INSERT INTO role_permissions (role_id, permission_id) "
            "SELECT %s, id FROM permissions WHERE code = ANY(%s)",
            (role_id, permission_codes),
        )
    return role_id


def grant(user_id, role_id, *, school=None, year=None, grade=None) -> UUID:
    grant_id = uuid4()
    with mig() as c:
        c.execute(
            "INSERT INTO user_roles (id, user_id, role_id, school_id, academic_year_id, grade_id)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (grant_id, user_id, role_id, school, year, grade),
        )
    return grant_id


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


def login(client: TestClient, email: str, password: str = PASSWORD, *, ua: str | None = None):
    headers = {"User-Agent": ua} if ua else {}
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}, headers=headers
    )


def user_row(user_id) -> dict:
    with mig() as c:
        status, failed, locked_until = c.execute(
            "SELECT status, failed_login_count, locked_until FROM users WHERE id = %s", (user_id,)
        ).fetchone()
        audits = c.execute(
            "SELECT count(*) FROM audit_logs WHERE actor_id = %s "
            "AND action = 'session:login_failed'",
            (user_id,),
        ).fetchone()[0]
    return {
        "status": status,
        "failed_login_count": failed,
        "locked_until_set": locked_until is not None,
        "login_failed_audit_rows": audits,
    }


def probe_pending_activation_and_admin_chosen_password(app) -> None:
    role = create_role("full", FULL)
    admin_id, admin_email = create_user("p1-admin")
    grant(admin_id, role)
    invitee_email = f"p1-invitee-{RUN}@example.com"
    admin_chosen = "Admin-Chosen-Password-9!"
    out: dict = {}
    with client_for(app) as admin:
        assert login(admin, admin_email).status_code == 200
        invited = admin.post(
            "/api/v1/admin/users/invitations",
            json={"email": invitee_email, "display_name": "Invitee"},
            headers=csrf(admin),
        )
        out["invite_http"] = invited.status_code
        body = invited.json()
        target, invite_token = body["user"]["id"], body["one_time_token"]
        out["status_after_invite"] = body["user"]["status"]
        activated = admin.patch(
            f"/api/v1/admin/users/{target}/status",
            json={"status": "active", "reason": "probe"},
            headers=csrf(admin),
        )
        out["activate_pending_http"] = activated.status_code
        out["status_after_activate"] = activated.json().get("status")
        out["invitee_accept_after_activate_http"] = admin.post(
            "/api/v1/auth/invitations/accept",
            json={"token": invite_token, "password": "Invitee-Chosen-Password-1!"},
        ).status_code
        reset = admin.post(
            f"/api/v1/admin/users/{target}/password-reset", json={}, headers=csrf(admin)
        )
        out["reset_issue_http"] = reset.status_code
        out["admin_accepts_reset_http"] = admin.post(
            "/api/v1/auth/password-reset/accept",
            json={"token": reset.json()["one_time_token"], "new_password": admin_chosen},
        ).status_code
    with client_for(app) as impersonation:
        out["login_as_target_with_admin_chosen_password_http"] = login(
            impersonation, invitee_email, admin_chosen
        ).status_code
    results["P1_pending_activation_then_admin_sets_password"] = out


def probe_password_reset_privilege_escalation(app) -> None:
    full = create_role("superior", FULL)
    reset_only = create_role("resetonly", ["user:password_reset"])
    suspend_only = create_role("suspendonly", ["user:suspend"])
    superior_id, superior_email = create_user("p2-superior-admin")
    grant(superior_id, full)
    helper_id, helper_email = create_user("p2-reset-only")
    grant(helper_id, reset_only)
    suspender_id, suspender_email = create_user("p2-suspend-only")
    grant(suspender_id, suspend_only)
    bystander_id, _ = create_user("p2-bystander")
    out: dict = {}
    with client_for(app) as helper:
        assert login(helper, helper_email).status_code == 200
        out["reset_only_actor_reads_user_http"] = helper.get(
            f"/api/v1/admin/users/{bystander_id}"
        ).status_code
        reset = helper.post(
            f"/api/v1/admin/users/{superior_id}/password-reset", json={}, headers=csrf(helper)
        )
        out["reset_only_actor_issues_reset_for_superior_http"] = reset.status_code
        out["reset_only_actor_accepts_http"] = helper.post(
            "/api/v1/auth/password-reset/accept",
            json={"token": reset.json()["one_time_token"], "new_password": "Taken-Over-Pass-7!"},
        ).status_code
    with client_for(app) as takeover:
        out["login_as_superior_http"] = login(
            takeover, superior_email, "Taken-Over-Pass-7!"
        ).status_code
        out["as_superior_reads_user_http"] = takeover.get(
            f"/api/v1/admin/users/{bystander_id}"
        ).status_code
    victim_id, _ = create_user("p2-superior-2")
    grant(victim_id, full)
    with client_for(app) as suspender:
        assert login(suspender, suspender_email).status_code == 200
        out["suspend_only_actor_suspends_superior_http"] = suspender.patch(
            f"/api/v1/admin/users/{victim_id}/status",
            json={"status": "suspended", "reason": "probe"},
            headers=csrf(suspender),
        ).status_code
    results["P2_password_reset_and_suspend_have_no_target_privilege_bound"] = out


async def _race(raw_token: str) -> dict:
    database = Database(SecretStr(RUNTIME_SQLA))
    limiter = LoginRateLimiter(limit=50, window_seconds=60)
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(login_rate_limiter=limiter)),
        client=SimpleNamespace(host="198.51.100.7"),
    )
    out: dict = {}
    async with database.session_factory() as session_a, database.session_factory() as session_b:
        token_a, _ = await _consume_account_token(
            db=session_a, raw_token=raw_token, purpose="password_reset", request=request
        )
        await session_a.execute(
            update(AccountToken).where(AccountToken.id == token_a.id).values(used_at=func.now())
        )
        await session_a.flush()

        async def second_request():
            try:
                token_b, _ = await _consume_account_token(
                    db=session_b, raw_token=raw_token, purpose="password_reset", request=request
                )
                return {"result": "accepted", "orm_used_at_seen_by_b": str(token_b.used_at)}
            except AppError as error:
                return {"result": "rejected", "code": error.code}

        task = asyncio.create_task(second_request())
        await asyncio.sleep(1.0)
        out["b_blocked_while_a_uncommitted"] = not task.done()
        await session_a.commit()
        out["b_after_a_commit"] = await asyncio.wait_for(task, 15)
        await session_b.rollback()
    async with database.session_factory() as session_c:
        try:
            await _consume_account_token(
                db=session_c, raw_token=raw_token, purpose="password_reset", request=request
            )
            out["sequential_reuse_after_commit"] = "accepted"
        except AppError as error:
            out["sequential_reuse_after_commit"] = error.code
    await database.close()
    return out


def probe_concurrent_token_reuse() -> None:
    user_id, _ = create_user("p3-reset-target")
    raw = generate_session_token()
    with mig() as c:
        c.execute(
            "INSERT INTO account_tokens (id, user_id, purpose, token_hash, expires_at, created_by)"
            " VALUES (%s, %s, 'password_reset', %s, now() + interval '1 hour', %s)",
            (uuid4(), user_id, hash_session_token(raw), user_id),
        )
    results["P3_concurrent_reset_token_consumption"] = asyncio.run(
        _race(raw), loop_factory=create_event_loop
    )


def probe_long_user_agent_lockout_bypass() -> None:
    long_ua = "Mozilla/5.0 " + "A" * 600
    out: dict = {}
    app = app_for()
    bypass_id, bypass_email = create_user("p4-bypass")
    with client_for(app) as client:
        out["eight_wrong_long_ua_http"] = [
            login(client, bypass_email, "wrong-password", ua=long_ua).status_code
            for _ in range(8)
        ]
    out["after_eight_wrong_long_ua"] = user_row(bypass_id)
    control_id, control_email = create_user("p4-control")
    with client_for(app) as client:
        out["five_wrong_normal_ua_http"] = [
            login(client, control_email, "wrong-password").status_code for _ in range(5)
        ]
    out["control_after_five_wrong_normal_ua"] = user_row(control_id)

    oracle_app = app_for(login_rate_limit_attempts=3, login_rate_limit_window_seconds=60)
    wrong_id, wrong_email = create_user("p4-oracle-wrong")
    right_id, right_email = create_user("p4-oracle-right")
    with client_for(oracle_app) as client:
        for _ in range(2):
            login(client, wrong_email, "known-wrong", ua=long_ua)
        guess_wrong = login(client, wrong_email, "candidate-wrong", ua=long_ua).status_code
        follow_wrong = login(client, wrong_email, "probe", ua=long_ua).status_code
        for _ in range(2):
            login(client, right_email, "known-wrong", ua=long_ua)
        guess_right = login(client, right_email, PASSWORD, ua=long_ua).status_code
        follow_right = login(client, right_email, "probe", ua=long_ua).status_code
    out["oracle_wrong_guess"] = {"guess_http": guess_wrong, "follow_up_http": follow_wrong}
    out["oracle_correct_guess"] = {"guess_http": guess_right, "follow_up_http": follow_right}
    out["oracle_accounts_after"] = {"wrong": user_row(wrong_id), "right": user_row(right_id)}
    results["P4_long_user_agent_rolls_back_lockout_and_audit"] = out


def probe_lockout_terminates_active_session() -> None:
    app = app_for()
    victim_id, victim_email = create_user("p5-victim")
    out: dict = {}
    with client_for(app) as victim, client_for(app) as attacker:
        assert login(victim, victim_email).status_code == 200
        out["victim_me_before_http"] = victim.get("/api/v1/auth/me").status_code
        out["attacker_wrong_attempts_http"] = [
            login(attacker, victim_email, "wrong-password").status_code for _ in range(5)
        ]
        after = victim.get("/api/v1/auth/me")
        out["victim_me_after_http"] = after.status_code
        out["victim_me_after_code"] = after.json()["error"]["code"]
    out["victim_row"] = user_row(victim_id)
    results["P5_unauthenticated_lockout_ends_existing_session"] = out


async def _loop_blocking() -> dict:
    import httpx2

    app = app_for()
    app.state.database = Database(SecretStr(RUNTIME_SQLA))
    transport = httpx2.ASGITransport(app=app)
    out: dict = {}
    async with httpx2.AsyncClient(transport=transport, base_url="https://testserver") as client:
        await client.get("/api/v1/health/live")
        start = time.perf_counter()
        await client.get("/api/v1/health/live")
        out["liveness_idle_ms"] = round((time.perf_counter() - start) * 1000, 1)

        async def failed_login(index: int):
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": f"p6-nobody-{index}-{RUN}@example.com", "password": "x"},
            )
            return response.status_code

        async def liveness_during_logins():
            await asyncio.sleep(0.02)
            begin = time.perf_counter()
            await client.get("/api/v1/health/live")
            return round((time.perf_counter() - begin) * 1000, 1)

        gathered = await asyncio.gather(
            *(failed_login(i) for i in range(10)), liveness_during_logins()
        )
        out["login_statuses"] = gathered[:-1]
        out["liveness_during_10_concurrent_logins_ms"] = gathered[-1]
    await app.state.database.close()
    return out


def probe_event_loop_blocking() -> None:
    results["P6_argon2_blocks_event_loop"] = asyncio.run(
        _loop_blocking(), loop_factory=create_event_loop
    )


def probe_delegation_outlives_delegator_validity() -> None:
    app = app_for()
    school, year = uuid4(), uuid4()
    scoped = create_role("scoped", ["user:read", "user:grant_role", "user:revoke_role"])
    delegator_id, delegator_email = create_user("p7-delegator")
    original = grant(delegator_id, scoped, school=school, year=year)
    with mig() as c:
        c.execute(
            "UPDATE user_roles SET valid_until = now() + interval '10 minutes' WHERE id = %s",
            (original,),
        )
    other_id, _ = create_user("p7-other")
    later_id, _ = create_user("p7-later")
    out: dict = {}
    with client_for(app) as delegator:
        assert login(delegator, delegator_email).status_code == 200
        out["grant_other_without_valid_until_http"] = delegator.post(
            f"/api/v1/admin/users/{other_id}/roles",
            json={"role_id": str(scoped), "school_id": str(school), "academic_year_id": str(year)},
            headers=csrf(delegator),
        ).status_code
        self_grant = delegator.post(
            f"/api/v1/admin/users/{delegator_id}/roles",
            json={
                "role_id": str(scoped), "school_id": str(school),
                "academic_year_id": str(year), "grade_id": 1,
            },
            headers=csrf(delegator),
        )
        out["self_grant_narrower_scope_without_valid_until_http"] = self_grant.status_code
        self_grant_id = self_grant.json().get("id")
        with mig() as c:
            c.execute(
                "UPDATE user_roles SET valid_until = now() - interval '1 minute' WHERE id = %s",
                (original,),
            )
        out["after_original_expiry_grant_school_year_http"] = delegator.post(
            f"/api/v1/admin/users/{later_id}/roles",
            json={"role_id": str(scoped), "school_id": str(school), "academic_year_id": str(year)},
            headers=csrf(delegator),
        ).status_code
        out["after_original_expiry_grant_grade1_http"] = delegator.post(
            f"/api/v1/admin/users/{later_id}/roles",
            json={
                "role_id": str(scoped), "school_id": str(school),
                "academic_year_id": str(year), "grade_id": 1,
            },
            headers=csrf(delegator),
        ).status_code
    with mig() as c:
        row = c.execute(
            "SELECT after_state FROM audit_logs WHERE action = 'user:grant_role' "
            "AND resource_id = %s",
            (self_grant_id,),
        ).fetchone()
    out["self_grant_audit_after_state_keys"] = sorted(row[0].keys()) if row else None
    results["P7_delegated_grants_outlive_delegator_validity"] = out


def probe_suspend_revokes_and_reinvite_dead_end() -> None:
    app = app_for()
    role = create_role("full2", FULL)
    admin_id, admin_email = create_user("p9-admin")
    grant(admin_id, role)
    member_id, member_email = create_user("p9-member")
    pending_email = f"p10-pending-{RUN}@example.com"
    out: dict = {}
    with client_for(app) as member, client_for(app) as admin:
        assert login(member, member_email).status_code == 200
        assert login(admin, admin_email).status_code == 200
        out["suspend_http"] = admin.patch(
            f"/api/v1/admin/users/{member_id}/status",
            json={"status": "suspended", "reason": "probe"},
            headers=csrf(admin),
        ).status_code
        out["member_me_after_suspend_http"] = member.get("/api/v1/auth/me").status_code
        invited = admin.post(
            "/api/v1/admin/users/invitations",
            json={"email": pending_email, "display_name": "Pending"},
            headers=csrf(admin),
        ).json()
        with mig() as c:
            c.execute(
                "UPDATE account_tokens SET expires_at = now() - interval '1 minute' "
                "WHERE user_id = %s",
                (invited["user"]["id"],),
            )
        out["reinvite_same_email_http"] = admin.post(
            "/api/v1/admin/users/invitations",
            json={"email": pending_email, "display_name": "Pending"},
            headers=csrf(admin),
        ).status_code
        reset = admin.post(
            f"/api/v1/admin/users/{invited['user']['id']}/password-reset",
            json={},
            headers=csrf(admin),
        )
        out["reset_for_pending_http"] = reset.status_code
        out["reset_for_pending_code"] = reset.json()["error"]["code"]
    with mig() as c:
        out["member_sessions_by_status"] = dict(
            c.execute(
                "SELECT status, count(*) FROM sessions WHERE user_id = %s GROUP BY status",
                (member_id,),
            ).fetchall()
        )
    results["P9_P10_suspend_revokes_sessions_and_pending_reinvite_dead_end"] = out


def probe_db_privileges() -> None:
    out: dict = {}
    with mig() as c:
        out["migrator_is_superuser"] = c.execute(
            "SELECT rolsuper FROM pg_roles WHERE rolname = current_user"
        ).fetchone()[0]
        out["runtime_account_tokens_sel_ins_upd__delete__truncate__worker_select"] = c.execute(
            "SELECT has_table_privilege('eduops_runtime','account_tokens','SELECT,INSERT,UPDATE'),"
            " has_table_privilege('eduops_runtime','account_tokens','DELETE'),"
            " has_table_privilege('eduops_runtime','account_tokens','TRUNCATE'),"
            " has_table_privilege('eduops_audit_worker','account_tokens','SELECT')"
        ).fetchone()
        c.execute("CREATE TABLE audit_probe_future_table (id integer)")
        try:
            out["runtime_has_any_privilege_on_new_table"] = c.execute(
                "SELECT has_table_privilege('eduops_runtime','audit_probe_future_table','SELECT')"
                " OR has_table_privilege('eduops_runtime','audit_probe_future_table','INSERT')"
            ).fetchone()[0]
        finally:
            c.execute("DROP TABLE audit_probe_future_table")
        out["database_acl"] = c.execute(
            "SELECT datacl::text FROM pg_database WHERE datname = current_database()"
        ).fetchone()[0]
    results["P11_database_privileges_at_head"] = out


if __name__ == "__main__":
    started = datetime.now().astimezone().isoformat()
    shared_app = app_for()
    probe_pending_activation_and_admin_chosen_password(shared_app)
    probe_password_reset_privilege_escalation(shared_app)
    probe_concurrent_token_reuse()
    probe_long_user_agent_lockout_bypass()
    probe_lockout_terminates_active_session()
    probe_event_loop_blocking()
    probe_delegation_outlives_delegator_validity()
    probe_suspend_revokes_and_reinvite_dead_end()
    probe_db_privileges()
    payload = {
        "started_at": started,
        "finished_at": datetime.now().astimezone().isoformat(),
        "run_suffix": RUN,
        "results": results,
    }
    OUT.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
