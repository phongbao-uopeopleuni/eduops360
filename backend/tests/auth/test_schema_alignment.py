"""Static regression checks for Phase 02 model/migration alignment."""

from __future__ import annotations

import importlib.util
import io
import re
from pathlib import Path
from types import ModuleType

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import configure_mappers
from sqlalchemy.sql.elements import TextClause

from app.modules.audit_logs.models import AuditLog, AuditOutbox
from app.modules.auth.models import (
    AccountToken,
    Permission,
    Role,
    RolePermission,
    Session,
    User,
    UserRole,
)

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def test_all_orm_relationships_configure_without_ambiguity() -> None:
    configure_mappers()


def _load_migration(filename: str) -> ModuleType:
    path = BACKEND_ROOT / "migrations" / "versions" / filename
    spec = importlib.util.spec_from_file_location(f"test_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Không thể tải migration: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _render_upgrade_sql(filename: str) -> str:
    module = _load_migration(filename)
    output = io.StringIO()
    context = MigrationContext.configure(
        dialect_name="postgresql",
        opts={"as_sql": True, "literal_binds": True, "output_buffer": output},
    )
    module.op = Operations(context)
    module.upgrade()
    return output.getvalue()


def _table_sql(sql: str, table: str) -> str:
    match = re.search(
        rf"CREATE TABLE {re.escape(table)} \((.*?)\n\);",
        sql,
        flags=re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"Không tìm thấy CREATE TABLE {table}")
    return match.group(1)


def _assert_not_null(sql: str, table: str, columns: tuple[str, ...]) -> None:
    body = _table_sql(sql, table)
    for column in columns:
        assert re.search(rf"\n\s*{re.escape(column)}\s+.*?NOT NULL", body), (
            f"{table}.{column} phải là NOT NULL trong migration"
        )


def _foreign_key_ondelete(model: type, column: str) -> str | None:
    foreign_keys = list(model.__table__.c[column].foreign_keys)
    assert len(foreign_keys) == 1, f"{model.__tablename__}.{column} phải có đúng một FK"
    return foreign_keys[0].ondelete


def test_required_migration_columns_are_not_nullable() -> None:
    auth_sql = _render_upgrade_sql("0002_auth_users.py")
    audit_sql = _render_upgrade_sql("0003_audit_logs.py")

    expected_auth = {
        "users": ("mfa_enabled", "failed_login_count", "created_at", "updated_at"),
        "roles": ("is_system", "created_at", "updated_at"),
        "permissions": ("requires_approval", "created_at"),
        "role_permissions": ("granted_at",),
        "user_roles": ("valid_from", "is_active", "granted_at"),
        "sessions": ("status", "created_at", "last_activity_at"),
    }
    for table, columns in expected_auth.items():
        _assert_not_null(auth_sql, table, columns)

    _assert_not_null(
        audit_sql,
        "audit_outbox",
        ("delivered", "delivery_attempts", "created_at"),
    )


def test_models_use_database_timestamp_expressions_and_jsonb() -> None:
    timestamp_columns = (
        User.__table__.c.created_at,
        User.__table__.c.updated_at,
        Role.__table__.c.created_at,
        Role.__table__.c.updated_at,
        Permission.__table__.c.created_at,
        RolePermission.__table__.c.granted_at,
        UserRole.__table__.c.valid_from,
        UserRole.__table__.c.granted_at,
        Session.__table__.c.created_at,
        Session.__table__.c.last_activity_at,
        AuditLog.__table__.c.created_at,
        AuditOutbox.__table__.c.created_at,
        AccountToken.__table__.c.created_at,
    )
    for column in timestamp_columns:
        assert column.server_default is not None
        assert isinstance(column.server_default.arg, TextClause), (
            f"{column.table.name}.{column.name} phải dùng biểu thức DB, không dùng chuỗi"
        )

    assert User.__table__.c.updated_at.onupdate is not None
    assert not callable(User.__table__.c.updated_at.onupdate.arg)
    assert Role.__table__.c.updated_at.onupdate is not None
    assert not callable(Role.__table__.c.updated_at.onupdate.arg)

    assert isinstance(AuditLog.__table__.c.before_state.type, JSONB)
    assert isinstance(AuditLog.__table__.c.after_state.type, JSONB)
    assert isinstance(AuditLog.__table__.c.extra_data.type, JSONB)


def test_history_foreign_keys_restrict_hard_delete() -> None:
    expected_model_fks = (
        (RolePermission, "granted_by"),
        (UserRole, "user_id"),
        (UserRole, "role_id"),
        (UserRole, "granted_by"),
        (UserRole, "revoked_by"),
        (Session, "user_id"),
        (AccountToken, "user_id"),
        (AccountToken, "created_by"),
        (AuditOutbox, "audit_log_id"),
    )
    for model, column in expected_model_fks:
        assert _foreign_key_ondelete(model, column) == "RESTRICT"

    auth_sql = _render_upgrade_sql("0002_auth_users.py")
    audit_sql = _render_upgrade_sql("0003_audit_logs.py")
    assert auth_sql.count("ON DELETE RESTRICT") >= 6
    assert audit_sql.count("ON DELETE RESTRICT") >= 1

    account_token_sql = _render_upgrade_sql("0007_account_tokens.py")
    _assert_not_null(
        account_token_sql,
        "account_tokens",
        ("user_id", "purpose", "token_hash", "expires_at", "created_by", "created_at"),
    )
    assert account_token_sql.count("ON DELETE RESTRICT") >= 2
    assert "GRANT SELECT, INSERT, UPDATE ON account_tokens TO eduops_runtime" in (account_token_sql)


def test_database_security_migration_is_deny_by_default() -> None:
    security_sql = _render_upgrade_sql("0004_database_security.py")

    assert "REVOKE CONNECT ON DATABASE" in security_sql
    assert "REVOKE ALL ON SCHEMA public FROM PUBLIC" in security_sql
    assert "REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC" in security_sql
    assert "GRANT SELECT, INSERT ON audit_logs TO eduops_runtime" in security_sql
    assert "GRANT SELECT, INSERT ON audit_outbox TO eduops_runtime" in security_sql
    assert "GRANT SELECT, UPDATE ON audit_outbox TO eduops_audit_worker" in security_sql
    assert not re.search(
        r"GRANT .*\b(?:UPDATE|DELETE|TRUNCATE)\b.* ON audit_logs",
        security_sql,
    )


def test_mfa_replay_counter_model_and_migration_align() -> None:
    assert User.__table__.c.mfa_last_used_step.nullable
    module = _load_migration("0008_mfa_replay_counter.py")
    assert module.down_revision == "0007_account_tokens"
