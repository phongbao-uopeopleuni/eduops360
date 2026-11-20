"""Pydantic schemas for timetable solver jobs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TeachingAssignmentInput(BaseModel):
    assignment_id: str = Field(min_length=1, max_length=100)
    teacher_id: str = Field(min_length=1, max_length=100)
    class_id: str = Field(min_length=1, max_length=100)
    subject_id: str = Field(min_length=1, max_length=100)
    room_id: str | None = Field(default=None, max_length=100)
    required_lessons: int = Field(ge=1, le=100)


class AvailableSlotInput(BaseModel):
    slot_id: str = Field(min_length=1, max_length=100)
    weekday: int = Field(ge=1, le=7)
    start_minute: int = Field(ge=0, le=1439)
    end_minute: int = Field(ge=1, le=1440)


class TimetableJobCreate(BaseModel):
    school_id: UUID
    academic_year_id: UUID
    assignments: list[TeachingAssignmentInput]
    slots: list[AvailableSlotInput]
    closed_slot_ids: list[str] = Field(default_factory=list)
    time_limit_seconds: int = Field(default=30, ge=1, le=300)
    random_seed: int = Field(default=360, ge=0, le=2147483647)


class TimetableJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: UUID
    academic_year_id: UUID
    status: str
    solver_status: str | None
    snapshot_checksum: str
    result: dict
    error: str | None
    time_limit_seconds: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class TimetableVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: UUID
    academic_year_id: UUID
    job_id: UUID
    revision: int
    status: str
    entries: list
    created_at: datetime
    published_at: datetime | None
