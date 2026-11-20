"""SQLAlchemy models for students, classes and enrollments.

Phase 03 — student identity and enrollment with immutable history.
DEC-002: Grades 1-12. DEC-005: minimal student record, stable ID.
"""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SchoolClass(Base):
    __tablename__ = "school_classes"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    homeroom_teacher_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="school_class", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("grade >= 1 AND grade <= 12", name="ck_school_classes_grade"),
        UniqueConstraint("school_id", "academic_year_id", "name", name="uq_school_classes_name"),
        Index("ix_school_classes_school_year", "school_id", "academic_year_id"),
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    student_code: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="student", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'graduated', 'withdrawn', 'transferred')",
            name="ck_students_status",
        ),
        UniqueConstraint("school_id", "student_code", name="uq_students_school_code"),
        Index("ix_students_school", "school_id"),
        Index("ix_students_full_name", "full_name"),
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("students.id", ondelete="RESTRICT"), nullable=False
    )
    school_class_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("school_classes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="enrolled")
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    school_class: Mapped["SchoolClass"] = relationship(back_populates="enrollments")

    __table_args__ = (
        CheckConstraint(
            "status IN ('enrolled', 'withdrawn', 'transferred')",
            name="ck_enrollments_status",
        ),
        UniqueConstraint(
            "student_id",
            "school_class_id",
            "academic_year_id",
            name="uq_enrollments_student_class_year",
        ),
        Index("ix_enrollments_student", "student_id"),
        Index("ix_enrollments_class", "school_class_id"),
        Index("ix_enrollments_year", "academic_year_id"),
    )


class StudentImportBatch(Base):
    __tablename__ = "student_import_batches"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
    )
    actor_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False, default="create_only")
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="preview")
    counts: Mapped[dict] = mapped_column("counts", JSONB, nullable=False, default=dict)
    error_report: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )
    committed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "mode IN ('create_only')",
            name="ck_student_import_batches_mode",
        ),
        CheckConstraint(
            "state IN ('preview', 'ready', 'committed', 'failed')",
            name="ck_student_import_batches_state",
        ),
        UniqueConstraint(
            "school_id",
            "actor_id",
            "idempotency_key",
            name="uq_student_import_batches_actor_key",
        ),
        Index(
            "ix_student_import_batches_scope",
            "school_id",
            "academic_year_id",
        ),
    )


class StudentImportRow(Base):
    __tablename__ = "student_import_rows"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    batch_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("student_import_batches.id", ondelete="CASCADE"),
        nullable=False,
    )
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    student_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    normalized_values: Mapped[dict] = mapped_column("normalized_values", JSONB, nullable=False)
    errors: Mapped[list] = mapped_column("errors", JSONB, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('valid', 'new', 'existing', 'conflicting', 'error')",
            name="ck_student_import_rows_status",
        ),
        UniqueConstraint("batch_id", "row_number", name="uq_student_import_rows_batch_row"),
        Index("ix_student_import_rows_batch_status", "batch_id", "status"),
    )
