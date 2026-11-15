"""Bind CSRF tokens to server-side sessions and normalize login identity.

Revision ID: 0005_secure_sessions
Revises: 0004_database_security
Create Date: 2026-11-13
"""

import sqlalchemy as sa
from alembic import op

revision = "0005_secure_sessions"
down_revision = "0004_database_security"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("sessions", sa.Column("csrf_token_hash", sa.String(64), nullable=True))
    op.execute("UPDATE sessions SET status = 'revoked', revoked_at = now()")
    op.create_index("uq_users_email_lower", "users", [sa.text("lower(email)")], unique=True)
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON sessions TO eduops_runtime")


def downgrade():
    op.drop_index("uq_users_email_lower", table_name="users")
    op.drop_column("sessions", "csrf_token_hash")
