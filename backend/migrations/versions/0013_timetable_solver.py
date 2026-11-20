"""Create timetable solver jobs and immutable version records.

Revision ID: 0013_timetable_solver
Revises: 0012_school_calendar
Create Date: 2026-11-20
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0013_timetable_solver"
down_revision = "0012_school_calendar"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "timetable_jobs",
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
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("solver_status", sa.String(20), nullable=True),
        sa.Column("snapshot_checksum", sa.String(64), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("result", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("time_limit_seconds", sa.Integer(), nullable=False, server_default="30"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed', 'cancelled')",
            name="ck_timetable_jobs_status",
        ),
        sa.CheckConstraint(
            "solver_status IS NULL OR solver_status IN "
            "('optimal', 'feasible', 'infeasible', 'unknown')",
            name="ck_timetable_jobs_solver_status",
        ),
        sa.CheckConstraint(
            "time_limit_seconds >= 1 AND time_limit_seconds <= 300",
            name="ck_timetable_jobs_time_limit",
        ),
    )
    op.create_index(
        "ix_timetable_jobs_scope",
        "timetable_jobs",
        ["school_id", "academic_year_id"],
    )

    op.create_table(
        "timetable_versions",
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
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("timetable_jobs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("entries", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("revision >= 1", name="ck_timetable_versions_revision"),
        sa.CheckConstraint(
            "status IN ('draft', 'approved', 'published', 'archived')",
            name="ck_timetable_versions_status",
        ),
    )
    op.create_index(
        "ix_timetable_versions_scope",
        "timetable_versions",
        ["school_id", "academic_year_id"],
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE ON TABLE timetable_jobs, timetable_versions TO eduops_runtime"
    )


def downgrade():
    op.drop_table("timetable_versions")
    op.drop_table("timetable_jobs")
