"""Models for the complete synthetic school academic dataset."""

from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    subject_group: Mapped[str] = mapped_column(String(50), nullable=False)
    __table_args__ = (
        UniqueConstraint("school_id", "source_id", name="uq_subjects_source"),
        UniqueConstraint("school_id", "code", name="uq_subjects_school_code"),
    )


class Teacher(Base):
    __tablename__ = "teachers"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    specialty_subject_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    __table_args__ = (
        UniqueConstraint("school_id", "source_id", name="uq_teachers_source"),
        UniqueConstraint("school_id", "code", name="uq_teachers_school_code"),
    )


class GradeSubject(Base):
    __tablename__ = "grade_subjects"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("academic_years.id", ondelete="RESTRICT"), nullable=False
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)
    __table_args__ = (
        CheckConstraint("grade >= 1 AND grade <= 12", name="ck_grade_subjects_grade"),
        CheckConstraint(
            "subject_type IN ('BAT_BUOC','LUA_CHON','TU_CHON')", name="ck_grade_subjects_type"
        ),
        UniqueConstraint(
            "school_id", "academic_year_id", "grade", "subject_id", name="uq_grade_subject"
        ),
    )


class TeachingAssignment(Base):
    __tablename__ = "teaching_assignments"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("academic_years.id", ondelete="RESTRICT"), nullable=False
    )
    class_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("school_classes.id", ondelete="RESTRICT"), nullable=False
    )
    subject_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    teacher_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("teachers.id", ondelete="RESTRICT"), nullable=False
    )
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint("semester IN (1,2)", name="ck_teaching_assignments_semester"),
        UniqueConstraint(
            "school_id",
            "academic_year_id",
            "class_id",
            "subject_id",
            "semester",
            name="uq_teaching_assignment",
        ),
    )


class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("academic_years.id", ondelete="RESTRICT"), nullable=False
    )
    student_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("students.id", ondelete="RESTRICT"), nullable=False
    )
    subject_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    assessment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    __table_args__ = (
        CheckConstraint("semester IN (1,2)", name="ck_assessments_semester"),
        CheckConstraint(
            "assessment_type IN ('THUONG_XUYEN','GIUA_KY','CUOI_KY')", name="ck_assessments_type"
        ),
        CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 10)", name="ck_assessments_score"
        ),
        UniqueConstraint("school_id", "source_id", name="uq_assessments_source"),
    )


class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("academic_years.id", ondelete="RESTRICT"), nullable=False
    )
    student_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("students.id", ondelete="RESTRICT"), nullable=False
    )
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    __table_args__ = (
        CheckConstraint(
            "status IN ('CO_MAT','VANG_CO_PHEP','VANG_KHONG_PHEP','DI_MUON')",
            name="ck_attendance_status",
        ),
        UniqueConstraint("student_id", "attendance_date", name="uq_attendance_student_date"),
    )
