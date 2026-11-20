"""Create student CSV import staging and idempotency tables.

Revision ID: 0011_student_import_staging
Revises: 0010_phase03_permissions
Create Date: 2026-11-20
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0011_student_import_staging"
down_revision = "0010_phase03_permissions"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "student_import_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "academic_year_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("academic_years.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False, server_default="create_only"),
        sa.Column("state", sa.String(20), nullable=False, server_default="preview"),
        sa.Column("counts", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("error_report", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("mode IN ('create_only')", name="ck_student_import_batches_mode"),
        sa.CheckConstraint(
            "state IN ('preview', 'ready', 'committed', 'failed')",
            name="ck_student_import_batches_state",
        ),
        sa.UniqueConstraint(
            "school_id",
            "actor_id",
            "idempotency_key",
            name="uq_student_import_batches_actor_key",
        ),
    )
    op.create_index(
        "ix_student_import_batches_scope",
        "student_import_batches",
        ["school_id", "academic_year_id"],
    )

    op.create_table(
        "student_import_rows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "batch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("student_import_batches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("student_code", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("normalized_values", postgresql.JSONB(), nullable=False),
        sa.Column("errors", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('valid', 'new', 'existing', 'conflicting', 'error')",
            name="ck_student_import_rows_status",
        ),
        sa.UniqueConstraint(
            "batch_id",
            "row_number",
            name="uq_student_import_rows_batch_row",
        ),
    )
    op.create_index(
        "ix_student_import_rows_batch_status",
        "student_import_rows",
        ["batch_id", "status"],
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE student_import_batches, "
        "student_import_rows TO eduops_runtime"
    )


def downgrade():
    op.drop_table("student_import_rows")
    op.drop_table("student_import_batches")
