"""Enforce unique timetable revision within each school and academic year.

Revision ID: 0015_timetable_revision
Revises: 0014_active_template
"""

from alembic import op

revision = "0015_timetable_revision"
down_revision = "0014_active_template"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_timetable_versions_scope_revision",
        "timetable_versions",
        ["school_id", "academic_year_id", "revision"],
    )


def downgrade():
    op.drop_constraint(
        "uq_timetable_versions_scope_revision",
        "timetable_versions",
        type_="unique",
    )
