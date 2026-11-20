"""SQLAlchemy models for schools, academic years and academic terms.

Phase 03 — master data and school hierarchy.
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
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="Asia/Ho_Chi_Minh")
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )

    academic_years: Mapped[list["AcademicYear"]] = relationship(
        back_populates="school", lazy="selectin"
    )


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )

    school: Mapped["School"] = relationship(back_populates="academic_years")
    terms: Mapped[list["AcademicTerm"]] = relationship(
        back_populates="academic_year", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("start_date < end_date", name="ck_academic_years_dates"),
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')", name="ck_academic_years_status"
        ),
        CheckConstraint("revision >= 0", name="ck_academic_years_revision"),
        UniqueConstraint("school_id", "name", name="uq_academic_years_school_name"),
        Index("ix_academic_years_school_status", "school_id", "status"),
    )


class AcademicTerm(Base):
    __tablename__ = "academic_terms"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    term_order: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )

    academic_year: Mapped["AcademicYear"] = relationship(back_populates="terms")

    __table_args__ = (
        CheckConstraint("start_date < end_date", name="ck_academic_terms_dates"),
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')", name="ck_academic_terms_status"
        ),
        CheckConstraint("term_order >= 1", name="ck_academic_terms_order"),
        UniqueConstraint("academic_year_id", "term_order", name="uq_academic_terms_year_order"),
        Index("ix_academic_terms_year", "academic_year_id"),
    )
