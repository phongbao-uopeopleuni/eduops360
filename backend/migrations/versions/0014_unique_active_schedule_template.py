"""Enforce exactly one active schedule template per school and academic year.

Revision ID: 0014_active_template
Revises: 0013_timetable_solver
Create Date: 2026-11-20
"""

from alembic import op

revision = "0014_active_template"
down_revision = "0013_timetable_solver"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE UNIQUE INDEX uq_schedule_templates_one_active_per_scope "
        "ON schedule_templates (school_id, academic_year_id) "
        "WHERE status = 'active'"
    )


def downgrade():
    op.execute("DROP INDEX uq_schedule_templates_one_active_per_scope")
