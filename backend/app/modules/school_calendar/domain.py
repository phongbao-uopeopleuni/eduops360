"""Pure domain values for school schedule templates and time slots."""

from dataclasses import dataclass
from datetime import time
from enum import StrEnum
from uuid import UUID


class DayOfWeek(StrEnum):
    """Locale-neutral day identifiers for a weekly schedule template."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class SchoolSession(StrEnum):
    """The two session partitions required by P05-T01."""

    AM = "am"
    PM = "pm"


@dataclass(frozen=True, slots=True)
class ScheduleSlot:
    """One weekly slot with date-free local wall-clock boundaries."""

    day_of_week: DayOfWeek
    session: SchoolSession
    start_time: time
    end_time: time


@dataclass(frozen=True, slots=True)
class ScheduleTemplate:
    """A weekly slot collection owned by one school and academic year."""

    school_id: UUID
    academic_year_id: UUID
    slots: tuple[ScheduleSlot, ...]
