"""Separate migrator, runtime and audit delivery database privileges.

Revision ID: 0004_database_security
Revises: 0003_audit_logs
Create Date: 2026-11-13

The login roles are provisioned outside Alembic by the deployment environment.
This migration fails closed when either required least-privilege role is absent.
"""

from alembic import op

revision = "0004_database_security"
down_revision = "0003_audit_logs"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DO $$
        DECLARE
            database_name text := current_database();
        BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_roles WHERE rolname = 'eduops_runtime'
            ) THEN
                RAISE EXCEPTION 'Required role eduops_runtime is not provisioned';
            END IF;
            IF NOT EXISTS (
                SELECT FROM pg_roles WHERE rolname = 'eduops_audit_worker'
            ) THEN
                RAISE EXCEPTION 'Required role eduops_audit_worker is not provisioned';
            END IF;

            EXECUTE format(
                'REVOKE CONNECT ON DATABASE %I FROM PUBLIC', database_name
            );
            EXECUTE format(
                'GRANT CONNECT ON DATABASE %I TO eduops_runtime, '
                'eduops_audit_worker',
                database_name
            );
        END
        $$
        """
    )

    op.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA public TO eduops_runtime")
    op.execute("GRANT USAGE ON SCHEMA public TO eduops_audit_worker")
    op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC")

    op.execute("GRANT SELECT, INSERT, UPDATE ON users TO eduops_runtime")
    op.execute("GRANT SELECT ON roles, permissions, role_permissions TO eduops_runtime")
    op.execute("GRANT SELECT, INSERT, UPDATE ON user_roles TO eduops_runtime")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON sessions TO eduops_runtime")
    op.execute("GRANT SELECT, INSERT ON audit_logs TO eduops_runtime")
    op.execute("GRANT SELECT, INSERT ON audit_outbox TO eduops_runtime")

    op.execute("GRANT SELECT ON audit_logs TO eduops_audit_worker")
    op.execute("GRANT SELECT, UPDATE ON audit_outbox TO eduops_audit_worker")

    op.execute(
        """
        DO $$
        BEGIN
            EXECUTE format(
                'ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA public '
                'REVOKE ALL ON TABLES FROM PUBLIC',
                current_user
            );
        END
        $$
        """
    )


def downgrade():
    op.execute("REVOKE ALL ON audit_outbox FROM eduops_audit_worker")
    op.execute("REVOKE ALL ON audit_logs FROM eduops_audit_worker")
    op.execute("REVOKE ALL ON audit_outbox FROM eduops_runtime")
    op.execute("REVOKE ALL ON audit_logs FROM eduops_runtime")
    op.execute("REVOKE ALL ON sessions FROM eduops_runtime")
    op.execute("REVOKE ALL ON user_roles FROM eduops_runtime")
    op.execute("REVOKE ALL ON role_permissions FROM eduops_runtime")
    op.execute("REVOKE ALL ON permissions FROM eduops_runtime")
    op.execute("REVOKE ALL ON roles FROM eduops_runtime")
    op.execute("REVOKE ALL ON users FROM eduops_runtime")
    op.execute("REVOKE USAGE ON SCHEMA public FROM eduops_audit_worker")
    op.execute("REVOKE USAGE ON SCHEMA public FROM eduops_runtime")
    op.execute(
        """
        DO $$
        DECLARE
            database_name text := current_database();
        BEGIN
            EXECUTE format(
                'REVOKE CONNECT ON DATABASE %I FROM eduops_runtime, '
                'eduops_audit_worker',
                database_name
            );
            EXECUTE format(
                'GRANT CONNECT ON DATABASE %I TO PUBLIC', database_name
            );
        END
        $$
        """
    )
    op.execute("GRANT USAGE ON SCHEMA public TO PUBLIC")
