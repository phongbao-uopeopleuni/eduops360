"""Live PostgreSQL checks for the Phase 02 database security boundary.

These tests are skipped unless all three synthetic integration DSNs are supplied.
They must only target an isolated, disposable database.
"""

from __future__ import annotations

import os
from contextlib import closing
from uuid import uuid4

import psycopg
import pytest
from psycopg import errors

MIGRATOR_DSN = os.getenv("EDUOPS_TEST_MIGRATOR_DSN")
RUNTIME_DSN = os.getenv("EDUOPS_TEST_RUNTIME_DSN")
AUDIT_WORKER_DSN = os.getenv("EDUOPS_TEST_AUDIT_WORKER_DSN")

pytestmark = pytest.mark.skipif(
    not all((MIGRATOR_DSN, RUNTIME_DSN, AUDIT_WORKER_DSN)),
    reason="isolated PostgreSQL security DSNs are not configured",
)


def _connect(dsn: str | None) -> psycopg.Connection:
    assert dsn is not None
    return psycopg.connect(dsn, autocommit=True)


def test_login_roles_are_non_privileged_and_grants_are_minimal() -> None:
    with closing(_connect(MIGRATOR_DSN)) as connection:
        role_rows = connection.execute(
            """
            SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolreplication,
                   rolbypassrls
            FROM pg_roles
            WHERE rolname IN ('eduops_runtime', 'eduops_audit_worker')
            ORDER BY rolname
            """
        ).fetchall()
        assert role_rows == [
            ("eduops_audit_worker", False, False, False, False, False),
            ("eduops_runtime", False, False, False, False, False),
        ]

        grants = connection.execute(
            """
            SELECT
                has_schema_privilege('eduops_runtime', 'public', 'USAGE'),
                has_schema_privilege('eduops_runtime', 'public', 'CREATE'),
                has_table_privilege('eduops_runtime', 'users', 'SELECT,INSERT,UPDATE'),
                has_table_privilege('eduops_runtime', 'users', 'DELETE'),
                has_table_privilege('eduops_runtime', 'audit_logs', 'SELECT,INSERT'),
                has_table_privilege('eduops_runtime', 'audit_logs', 'UPDATE,DELETE,TRUNCATE'),
                has_table_privilege('eduops_audit_worker', 'audit_outbox', 'SELECT,UPDATE'),
                has_table_privilege('eduops_audit_worker', 'audit_outbox', 'INSERT,DELETE,TRUNCATE')
            """
        ).fetchone()
        assert grants == (True, False, True, False, True, False, True, False)


def test_runtime_and_audit_worker_cannot_mutate_source_audit_records() -> None:
    with closing(_connect(RUNTIME_DSN)) as runtime:
        for statement in (
            "CREATE TABLE forbidden_runtime_table (id integer)",
            "UPDATE audit_logs SET reason = 'forbidden' WHERE false",
            "DELETE FROM audit_logs WHERE false",
            "TRUNCATE audit_logs",
        ):
            with pytest.raises(errors.InsufficientPrivilege):
                runtime.execute(statement)

    with closing(_connect(AUDIT_WORKER_DSN)) as worker:
        for statement in (
            "INSERT INTO audit_logs (id, action, resource_type) "
            "VALUES (gen_random_uuid(), 'forbidden', 'test')",
            "UPDATE audit_logs SET reason = 'forbidden' WHERE false",
            "DELETE FROM audit_logs WHERE false",
            "TRUNCATE audit_logs",
        ):
            with pytest.raises(errors.InsufficientPrivilege):
                worker.execute(statement)


def test_runtime_audit_write_and_failed_audit_rollback_are_transactional() -> None:
    audit_id = uuid4()
    outbox_id = uuid4()
    rollback_user_id = uuid4()
    rollback_email = f"rollback-{rollback_user_id}@example.invalid"

    with closing(_connect(RUNTIME_DSN)) as runtime:
        with runtime.transaction():
            runtime.execute(
                """
                INSERT INTO audit_logs (id, action, resource_type, reason)
                VALUES (%s, 'security_test', 'synthetic', 'EDU-0024')
                """,
                (audit_id,),
            )
            runtime.execute(
                "INSERT INTO audit_outbox (id, audit_log_id) VALUES (%s, %s)",
                (outbox_id, audit_id),
            )

        with pytest.raises(errors.NotNullViolation):
            with runtime.transaction():
                runtime.execute(
                    """
                    INSERT INTO users (id, email, password_hash, display_name)
                    VALUES (%s, %s, 'synthetic-hash', 'Rollback Test')
                    """,
                    (rollback_user_id, rollback_email),
                )
                runtime.execute(
                    "INSERT INTO audit_logs (id, action, resource_type) "
                    "VALUES (%s, NULL, 'synthetic')",
                    (uuid4(),),
                )

    with closing(_connect(MIGRATOR_DSN)) as migrator:
        assert migrator.execute(
            "SELECT count(*) FROM users WHERE id = %s", (rollback_user_id,)
        ).fetchone() == (0,)
        assert migrator.execute(
            "SELECT count(*) FROM audit_outbox WHERE id = %s", (outbox_id,)
        ).fetchone() == (1,)
        migrator.execute("DELETE FROM audit_outbox WHERE id = %s", (outbox_id,))
        migrator.execute("DELETE FROM audit_logs WHERE id = %s", (audit_id,))
