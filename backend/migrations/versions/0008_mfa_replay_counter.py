"""Add the last accepted TOTP step for replay prevention.

Revision ID: 0008_mfa_replay_counter
Revises: 0007_account_tokens
Create Date: 2026-11-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0008_mfa_replay_counter"
down_revision = "0007_account_tokens"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("mfa_last_used_step", sa.BigInteger(), nullable=True),
    )


def downgrade():
    op.drop_column("users", "mfa_last_used_step")
