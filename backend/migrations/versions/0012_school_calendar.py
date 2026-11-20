"""Create school calendar templates, slots and holiday ranges.

Revision ID: 0012_school_calendar
Revises: 0011_student_import_staging
Create Date: 2026-11-20
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0012_school_calendar"
down_revision = "0011_student_import_staging"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "schedule_templates",
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
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
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
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_schedule_templates_status",
        ),
        sa.CheckConstraint("revision >= 1", name="ck_schedule_templates_revision"),
        sa.UniqueConstraint(
            "school_id",
            "academic_year_id",
            "name",
            "revision",
            name="uq_schedule_templates_scope_name_revision",
        ),
    )
    op.create_index(
        "ix_schedule_templates_scope",
        "schedule_templates",
        ["school_id", "academic_year_id"],
    )

    op.create_table(
        "schedule_slots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schedule_templates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("period", sa.String(5), nullable=False),
        sa.Column("start_time", sa.Time(timezone=False), nullable=False),
        sa.Column("end_time", sa.Time(timezone=False), nullable=False),
        sa.Column("slot_order", sa.Integer(), nullable=False),
        sa.CheckConstraint("weekday >= 1 AND weekday <= 7", name="ck_schedule_slots_weekday"),
        sa.CheckConstraint("period IN ('AM', 'PM')", name="ck_schedule_slots_period"),
        sa.CheckConstraint("start_time < end_time", name="ck_schedule_slots_interval"),
        sa.CheckConstraint("slot_order >= 1", name="ck_schedule_slots_order"),
        sa.UniqueConstraint(
            "template_id",
            "weekday",
            "slot_order",
            name="uq_schedule_slots_template_weekday_order",
        ),
    )
    op.create_index(
        "ix_schedule_slots_template_weekday",
        "schedule_slots",
        ["template_id", "weekday"],
    )

    op.create_table(
        "school_holidays",
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
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("source_reference", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
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
        sa.CheckConstraint("start_date <= end_date", name="ck_school_holidays_range"),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_school_holidays_status",
        ),
    )
    op.create_index(
        "ix_school_holidays_scope_dates",
        "school_holidays",
        ["school_id", "academic_year_id", "start_date", "end_date"],
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE schedule_templates, "
        "schedule_slots, school_holidays TO eduops_runtime"
    )


def downgrade():
    op.drop_table("school_holidays")
    op.drop_table("schedule_slots")
    op.drop_table("schedule_templates")
