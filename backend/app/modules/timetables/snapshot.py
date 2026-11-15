"""Immutable input projections for a future timetable solver."""

from dataclasses import dataclass
from datetime import date, time
from uuid import UUID

from app.modules.school_calendar.domain import DayOfWeek, SchoolSession


class MutableSnapshotCollectionError(TypeError):
    """Raised when a snapshot receives a mutable collection."""


@dataclass(frozen=True, slots=True)
class TeachingAssignmentSnapshot:
    assignment_id: UUID
    teacher_id: UUID
    class_group_id: UUID
    subject_id: UUID
    required_weekly_lessons: int


@dataclass(frozen=True, slots=True)
class ClassroomSnapshot:
    classroom_id: UUID
    capacity: int


@dataclass(frozen=True, slots=True)
class ClassGroupLoadSnapshot:
    class_group_id: UUID
    student_count: int


@dataclass(frozen=True, slots=True)
class ScheduleSlotSnapshot:
    slot_id: UUID
    day_of_week: DayOfWeek
    session: SchoolSession
    start_time: time
    end_time: time


@dataclass(frozen=True, slots=True)
class HolidaySnapshot:
    holiday_id: UUID
    start_date: date
    end_date: date
    start_time: time | None
    end_time: time | None


@dataclass(frozen=True, slots=True)
class SchedulingInputSnapshot:
    """A self-contained solver input for exactly one school and academic year."""

    snapshot_id: UUID
    school_id: UUID
    academic_year_id: UUID
    teaching_assignments: tuple[TeachingAssignmentSnapshot, ...]
    classrooms: tuple[ClassroomSnapshot, ...]
    class_group_loads: tuple[ClassGroupLoadSnapshot, ...]
    slots: tuple[ScheduleSlotSnapshot, ...]
    holidays: tuple[HolidaySnapshot, ...]

    def __post_init__(self) -> None:
        collection_names = (
            "teaching_assignments",
            "classrooms",
            "class_group_loads",
            "slots",
            "holidays",
        )
        for name in collection_names:
            if not isinstance(getattr(self, name), tuple):
                raise MutableSnapshotCollectionError(f"{name} must be an immutable tuple")
