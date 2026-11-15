"""Add explicit permissions required by the Phase 02 admin API.

Revision ID: 0006_admin_permissions
Revises: 0005_secure_sessions
Create Date: 2026-11-13

Role-to-permission policy remains intentionally unseeded pending OD-008 approval.
"""

from alembic import op

revision = "0006_admin_permissions"
down_revision = "0005_secure_sessions"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO permissions (
            id, code, resource_type, action, requires_approval, description_vi
        ) VALUES (
            gen_random_uuid(), 'user:activate', 'user', 'activate', FALSE,
            'Kích hoạt lại tài khoản'
        )
        ON CONFLICT (code) DO NOTHING
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM permissions
        WHERE code = 'user:activate'
          AND NOT EXISTS (
              SELECT 1 FROM role_permissions
              WHERE permission_id = permissions.id
          )
        """
    )
