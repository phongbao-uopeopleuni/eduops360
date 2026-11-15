"""Add hashed, expiring account invitation and password-reset tokens.

Revision ID: 0007_account_tokens
Revises: 0006_admin_permissions
Create Date: 2026-11-13
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_account_tokens"
down_revision = "0006_admin_permissions"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "account_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("purpose", sa.String(20), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "purpose IN ('invitation', 'password_reset')",
            name="ck_account_tokens_purpose",
        ),
    )
    op.create_index(
        "ix_account_tokens_user_purpose",
        "account_tokens",
        ["user_id", "purpose"],
    )
    op.create_index("ix_account_tokens_expires", "account_tokens", ["expires_at"])
    op.execute("GRANT SELECT, INSERT, UPDATE ON account_tokens TO eduops_runtime")
    op.execute(
        """
        INSERT INTO permissions (
            id, code, resource_type, action, requires_approval, description_vi
        ) VALUES (
            gen_random_uuid(), 'user:password_reset', 'user', 'password_reset',
            FALSE, 'Phát hành yêu cầu đặt lại mật khẩu'
        )
        ON CONFLICT (code) DO NOTHING
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM permissions
        WHERE code = 'user:password_reset'
          AND NOT EXISTS (
              SELECT 1 FROM role_permissions
              WHERE permission_id = permissions.id
          )
        """
    )
    op.drop_table("account_tokens")
