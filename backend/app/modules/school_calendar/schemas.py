"""Pydantic schemas for school calendar APIs."""

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScheduleSlotCreate(BaseModel):
    weekday: int = Field(ge=1, le=7)
    label: str = Field(min_length=1, max_length=100)
    period: str = Field(pattern=r"^(AM|PM)$")
    start_time: time
    end_time: time
    slot_order: int = Field(ge=1)


class ScheduleSlotRead(ScheduleSlotCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class ScheduleTemplateCreate(BaseModel):
    school_id: UUID
    academic_year_id: UUID
    name: str = Field(min_length=1, max_length=100)
    slots: list[ScheduleSlotCreate] = Field(default_factory=list)


class ScheduleTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: UUID
    academic_year_id: UUID
    name: str
    status: str
    revision: int
    created_at: datetime
    updated_at: datetime


class SchoolHolidayCreate(BaseModel):
    school_id: UUID
    academic_year_id: UUID
    name: str = Field(min_length=1, max_length=200)
    start_date: date
    end_date: date
    source_reference: str | None = Field(default=None, max_length=1000)


class SchoolHolidayRead(SchoolHolidayCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
