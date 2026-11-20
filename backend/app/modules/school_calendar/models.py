"""SQLAlchemy models for school calendars, time slots and holidays."""

from datetime import date, datetime, time
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
    Time,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScheduleTemplate(Base):
    __tablename__ = "schedule_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_schedule_templates_status",
        ),
        CheckConstraint("revision >= 1", name="ck_schedule_templates_revision"),
        UniqueConstraint(
            "school_id",
            "academic_year_id",
            "name",
            "revision",
            name="uq_schedule_templates_scope_name_revision",
        ),
        Index(
            "ix_schedule_templates_scope",
            "school_id",
            "academic_year_id",
        ),
    )


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("schedule_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    period: Mapped[str] = mapped_column(String(5), nullable=False)
    start_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    end_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    slot_order: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("weekday >= 1 AND weekday <= 7", name="ck_schedule_slots_weekday"),
        CheckConstraint(
            "period IN ('AM', 'PM')",
            name="ck_schedule_slots_period",
        ),
        CheckConstraint("start_time < end_time", name="ck_schedule_slots_interval"),
        CheckConstraint("slot_order >= 1", name="ck_schedule_slots_order"),
        UniqueConstraint(
            "template_id",
            "weekday",
            "slot_order",
            name="uq_schedule_slots_template_weekday_order",
        ),
        Index("ix_schedule_slots_template_weekday", "template_id", "weekday"),
    )


class SchoolHoliday(Base):
    __tablename__ = "school_holidays"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    school_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("start_date <= end_date", name="ck_school_holidays_range"),
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_school_holidays_status",
        ),
        Index(
            "ix_school_holidays_scope_dates",
            "school_id",
            "academic_year_id",
            "start_date",
            "end_date",
        ),
    )
