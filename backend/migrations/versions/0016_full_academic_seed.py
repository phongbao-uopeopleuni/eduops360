"""Add full synthetic academic seed tables.

Revision ID: 0016_full_academic_seed
Revises: 0015_timetable_revision
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0016_full_academic_seed"
down_revision = "0015_timetable_revision"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("subject_group", sa.String(50), nullable=False),
        sa.UniqueConstraint("school_id", "source_id", name="uq_subjects_source"),
        sa.UniqueConstraint("school_id", "code", name="uq_subjects_school_code"),
    )
    op.create_table(
        "teachers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "school_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("schools.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column(
            "specialty_subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.UniqueConstraint("school_id", "source_id", name="uq_teachers_source"),
        sa.UniqueConstraint("school_id", "code", name="uq_teachers_school_code"),
    )
    op.create_table(
        "grade_subjects",
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
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("subject_type", sa.String(20), nullable=False),
        sa.CheckConstraint("grade >= 1 AND grade <= 12", name="ck_grade_subjects_grade"),
        sa.CheckConstraint(
            "subject_type IN ('BAT_BUOC','LUA_CHON','TU_CHON')", name="ck_grade_subjects_type"
        ),
        sa.UniqueConstraint(
            "school_id", "academic_year_id", "grade", "subject_id", name="uq_grade_subject"
        ),
    )
    op.create_table(
        "teaching_assignments",
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
            "class_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("school_classes.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "teacher_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teachers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.CheckConstraint("semester IN (1,2)", name="ck_teaching_assignments_semester"),
        sa.UniqueConstraint(
            "school_id",
            "academic_year_id",
            "class_id",
            "subject_id",
            "semester",
            name="uq_teaching_assignment",
        ),
    )
    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
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
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.Column("assessment_type", sa.String(20), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("result_label", sa.String(100), nullable=True),
        sa.Column("exam_date", sa.Date(), nullable=True),
        sa.CheckConstraint("semester IN (1,2)", name="ck_assessments_semester"),
        sa.CheckConstraint(
            "assessment_type IN ('THUONG_XUYEN','GIUA_KY','CUOI_KY')", name="ck_assessments_type"
        ),
        sa.CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 10)", name="ck_assessments_score"
        ),
        sa.UniqueConstraint("school_id", "source_id", name="uq_assessments_source"),
    )
    op.create_table(
        "attendance",
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
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.CheckConstraint(
            "status IN ('CO_MAT','VANG_CO_PHEP','VANG_KHONG_PHEP','DI_MUON')",
            name="ck_attendance_status",
        ),
        sa.UniqueConstraint("student_id", "attendance_date", name="uq_attendance_student_date"),
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE subjects, teachers, "
        "grade_subjects, teaching_assignments, assessments, attendance TO eduops_runtime"
    )
    op.execute(
        """
        CREATE FUNCTION eduops_validate_academic_scope() RETURNS trigger AS $$
        BEGIN
          IF TG_TABLE_NAME = 'teachers' AND NEW.specialty_subject_id IS NOT NULL THEN
            IF NOT EXISTS (
              SELECT 1 FROM subjects
              WHERE id = NEW.specialty_subject_id AND school_id = NEW.school_id
            ) THEN RAISE EXCEPTION 'teacher specialty subject is outside school'; END IF;
          ELSIF TG_TABLE_NAME = 'grade_subjects' THEN
            IF NOT EXISTS (
              SELECT 1 FROM subjects
              WHERE id = NEW.subject_id AND school_id = NEW.school_id
            ) OR NOT EXISTS (
              SELECT 1 FROM academic_years
              WHERE id = NEW.academic_year_id AND school_id = NEW.school_id
            ) THEN RAISE EXCEPTION 'grade subject is outside school'; END IF;
          ELSIF TG_TABLE_NAME = 'teaching_assignments' THEN
            IF NOT EXISTS (
              SELECT 1 FROM academic_years
              WHERE id = NEW.academic_year_id AND school_id = NEW.school_id
            ) OR NOT EXISTS (
              SELECT 1 FROM school_classes
              WHERE id = NEW.class_id
                AND school_id = NEW.school_id
                AND academic_year_id = NEW.academic_year_id
            ) OR NOT EXISTS (
              SELECT 1 FROM subjects
              WHERE id = NEW.subject_id AND school_id = NEW.school_id
            ) OR NOT EXISTS (
              SELECT 1 FROM teachers
              WHERE id = NEW.teacher_id AND school_id = NEW.school_id
            ) THEN RAISE EXCEPTION 'teaching assignment is outside scope'; END IF;
          ELSIF TG_TABLE_NAME IN ('assessments', 'attendance') THEN
            IF NOT EXISTS (
              SELECT 1 FROM academic_years
              WHERE id = NEW.academic_year_id AND school_id = NEW.school_id
            ) OR NOT EXISTS (
              SELECT 1 FROM students
              WHERE id = NEW.student_id AND school_id = NEW.school_id
            ) OR NOT EXISTS (
              SELECT 1 FROM enrollments
              WHERE student_id = NEW.student_id
                AND academic_year_id = NEW.academic_year_id
            ) THEN RAISE EXCEPTION 'academic record is outside school'; END IF;
            IF TG_TABLE_NAME = 'assessments' AND NOT EXISTS (
              SELECT 1 FROM subjects
              WHERE id = NEW.subject_id AND school_id = NEW.school_id
            ) THEN RAISE EXCEPTION 'assessment subject is outside school'; END IF;
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    for table_name in (
        "teachers",
        "grade_subjects",
        "teaching_assignments",
        "assessments",
        "attendance",
    ):
        op.execute(
            f"CREATE TRIGGER trg_{table_name}_scope "
            f"BEFORE INSERT OR UPDATE ON {table_name} "
            "FOR EACH ROW EXECUTE FUNCTION eduops_validate_academic_scope()"
        )


def downgrade():
    for table_name in (
        "teachers",
        "grade_subjects",
        "teaching_assignments",
        "assessments",
        "attendance",
    ):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_scope ON {table_name}")
    op.execute("DROP FUNCTION IF EXISTS eduops_validate_academic_scope()")
    op.drop_table("attendance")
    op.drop_table("assessments")
    op.drop_table("teaching_assignments")
    op.drop_table("grade_subjects")
    op.drop_table("teachers")
    op.drop_table("subjects")
