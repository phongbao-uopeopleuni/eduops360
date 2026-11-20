"""Create Phase 03 tables: schools, academic years/terms, classes, students, enrollments.

Revision ID: 0009_phase03_school_student
Revises: 0008_mfa_replay_counter
Create Date: 2026-11-19
"""

import sqlalchemy as sa
from alembic import op

revision = "0009_phase03_school_student"
down_revision = "0008_mfa_replay_counter"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "schools",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("timezone", sa.String(100), nullable=False, server_default="Asia/Ho_Chi_Minh"),
        sa.Column("address", sa.Text(), nullable=True),
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
    )

    op.create_table(
        "academic_years",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="0"),
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
        sa.CheckConstraint("start_date < end_date", name="ck_academic_years_dates"),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived')", name="ck_academic_years_status"
        ),
        sa.CheckConstraint("revision >= 0", name="ck_academic_years_revision"),
        sa.UniqueConstraint("school_id", "name", name="uq_academic_years_school_name"),
    )
    op.create_index("ix_academic_years_school_status", "academic_years", ["school_id", "status"])

    op.create_table(
        "academic_terms",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "academic_year_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("academic_years.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("term_order", sa.Integer(), nullable=False),
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
        sa.CheckConstraint("start_date < end_date", name="ck_academic_terms_dates"),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived')", name="ck_academic_terms_status"
        ),
        sa.CheckConstraint("term_order >= 1", name="ck_academic_terms_order"),
        sa.UniqueConstraint("academic_year_id", "term_order", name="uq_academic_terms_year_order"),
    )
    op.create_index("ix_academic_terms_year", "academic_terms", ["academic_year_id"])

    op.create_table(
        "school_classes",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "academic_year_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("academic_years.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("homeroom_teacher_name", sa.String(200), nullable=True),
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
        sa.CheckConstraint("grade >= 1 AND grade <= 12", name="ck_school_classes_grade"),
        sa.UniqueConstraint("school_id", "academic_year_id", "name", name="uq_school_classes_name"),
    )
    op.create_index(
        "ix_school_classes_school_year", "school_classes", ["school_id", "academic_year_id"]
    )

    op.create_table(
        "students",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("student_code", sa.Text(), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
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
            "status IN ('active', 'graduated', 'withdrawn', 'transferred')",
            name="ck_students_status",
        ),
        sa.UniqueConstraint("school_id", "student_code", name="uq_students_school_code"),
    )
    op.create_index("ix_students_school", "students", ["school_id"])
    op.create_index("ix_students_full_name", "students", ["full_name"])

    op.create_table(
        "enrollments",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "student_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "school_class_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("school_classes.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "academic_year_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("academic_years.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="enrolled"),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
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
            "status IN ('enrolled', 'withdrawn', 'transferred')",
            name="ck_enrollments_status",
        ),
        sa.UniqueConstraint(
            "student_id",
            "school_class_id",
            "academic_year_id",
            name="uq_enrollments_student_class_year",
        ),
    )
    op.create_index("ix_enrollments_student", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_class", "enrollments", ["school_class_id"])
    op.create_index("ix_enrollments_year", "enrollments", ["academic_year_id"])

    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE schools, academic_years, "
        "academic_terms, school_classes, students, enrollments TO eduops_runtime"
    )


def downgrade():
    op.drop_table("enrollments")
    op.drop_table("students")
    op.drop_table("school_classes")
    op.drop_table("academic_terms")
    op.drop_table("academic_years")
    op.drop_table("schools")
