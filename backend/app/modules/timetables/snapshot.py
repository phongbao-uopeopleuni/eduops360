"""Immutable input projections for a future timetable solver."""

from dataclasses import dataclass
from datetime import date, time
from uuid import UUID

from app.common.domain_values import validate_scalar_fields
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

    def __post_init__(self) -> None:
        validate_scalar_fields(self)


@dataclass(frozen=True, slots=True)
class ClassroomSnapshot:
    classroom_id: UUID
    capacity: int

    def __post_init__(self) -> None:
        validate_scalar_fields(self)


@dataclass(frozen=True, slots=True)
class ClassGroupLoadSnapshot:
    class_group_id: UUID
    student_count: int

    def __post_init__(self) -> None:
        validate_scalar_fields(self)


@dataclass(frozen=True, slots=True)
class ScheduleSlotSnapshot:
    slot_id: UUID
    day_of_week: DayOfWeek
    session: SchoolSession
    start_time: time
    end_time: time

    def __post_init__(self) -> None:
        validate_scalar_fields(self)


@dataclass(frozen=True, slots=True)
class HolidaySnapshot:
    holiday_id: UUID
    start_date: date
    end_date: date
    start_time: time | None
    end_time: time | None

    def __post_init__(self) -> None:
        validate_scalar_fields(self)


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
        collection_types = {
            "teaching_assignments": TeachingAssignmentSnapshot,
            "classrooms": ClassroomSnapshot,
            "class_group_loads": ClassGroupLoadSnapshot,
            "slots": ScheduleSlotSnapshot,
            "holidays": HolidaySnapshot,
        }
        for name, element_type in collection_types.items():
            if not isinstance(getattr(self, name), tuple):
                raise MutableSnapshotCollectionError(f"{name} must be an immutable tuple")
            if any(type(item) is not element_type for item in getattr(self, name)):
                raise TypeError(f"{name} must contain only {element_type.__name__} values")
