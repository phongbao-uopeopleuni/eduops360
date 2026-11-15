"""Pure domain constraints for schools, academic years and academic terms."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class AcademicYearDomainError(ValueError):
    """Base error for academic-year domain validation."""


class InvalidDateRangeError(AcademicYearDomainError):
    """Raised when a date window does not have a positive duration."""


class TermOutsideYearError(AcademicYearDomainError):
    """Raised when an academic term is not fully inside its academic year."""


class InvalidStateTransitionError(AcademicYearDomainError):
    """Raised when a lifecycle transition is not explicitly allowed."""


class ParentYearStateError(AcademicYearDomainError):
    """Raised when a term transition conflicts with its parent year state."""


class ActiveYearConflictError(AcademicYearDomainError):
    """Raised when activating a year would create two active years in one school."""


class ArchivedYearReadOnlyError(AcademicYearDomainError):
    """Raised when a mutation targets an archived academic year."""


class ScopeMismatchError(AcademicYearDomainError):
    """Raised when a resource is outside the authorized school/year context."""


class RevisionConflictError(AcademicYearDomainError):
    """Raised when optimistic concurrency information is missing or stale."""


class InvalidTimezoneError(AcademicYearDomainError):
    """Raised when the school timezone is blank or is not an IANA timezone."""


class AcademicYearStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class AcademicTermStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


ACADEMIC_YEAR_TRANSITIONS = frozenset(
    {
        (AcademicYearStatus.DRAFT, AcademicYearStatus.ACTIVE),
        (AcademicYearStatus.ACTIVE, AcademicYearStatus.ARCHIVED),
    }
)

ACADEMIC_TERM_TRANSITIONS = frozenset(
    {
        (AcademicTermStatus.DRAFT, AcademicTermStatus.ACTIVE),
        (AcademicTermStatus.ACTIVE, AcademicTermStatus.ARCHIVED),
    }
)


@dataclass(frozen=True, slots=True)
class DateWindow:
    """Inclusive calendar-date boundaries with a strictly positive duration."""

    start_date: date
    end_date: date

    def __post_init__(self) -> None:
        if self.start_date >= self.end_date:
            raise InvalidDateRangeError("start_date must be before end_date")


def validate_term_window(*, term: DateWindow, academic_year: DateWindow) -> None:
    """Require both term boundaries to be contained by the academic year."""
    if term.start_date < academic_year.start_date or term.end_date > academic_year.end_date:
        raise TermOutsideYearError("academic term must be fully inside its academic year")


def ensure_academic_year_transition(
    current: AcademicYearStatus, target: AcademicYearStatus
) -> None:
    """Allow only the explicit forward academic-year lifecycle."""
    if (current, target) not in ACADEMIC_YEAR_TRANSITIONS:
        raise InvalidStateTransitionError(f"academic year cannot transition {current} -> {target}")


def ensure_academic_term_transition(
    current: AcademicTermStatus,
    target: AcademicTermStatus,
    *,
    parent_year_status: AcademicYearStatus,
) -> None:
    """Validate a term transition without weakening parent-year immutability."""
    if parent_year_status is AcademicYearStatus.ARCHIVED:
        raise ArchivedYearReadOnlyError("terms in an archived year are read-only")
    if target is AcademicTermStatus.ACTIVE and parent_year_status is not AcademicYearStatus.ACTIVE:
        raise ParentYearStateError("a term can become active only while its year is active")
    if (current, target) not in ACADEMIC_TERM_TRANSITIONS:
        raise InvalidStateTransitionError(f"academic term cannot transition {current} -> {target}")


def ensure_can_activate_academic_year(
    candidate_year_id: UUID, *, active_year_id: UUID | None
) -> None:
    """Reject activation when another year is already active for the school."""
    if active_year_id is not None and active_year_id != candidate_year_id:
        raise ActiveYearConflictError("the school already has a different active academic year")


def ensure_year_mutable(status: AcademicYearStatus) -> None:
    """Protect archived academic-year history from mutation."""
    if status is AcademicYearStatus.ARCHIVED:
        raise ArchivedYearReadOnlyError("archived academic years are read-only")


def ensure_year_scope(
    *,
    authorized_school_id: UUID | None,
    authorized_year_id: UUID | None,
    resource_school_id: UUID | None,
    resource_year_id: UUID | None,
) -> None:
    """Fail closed unless both school and academic-year scope match exactly."""
    if (
        authorized_school_id is None
        or authorized_year_id is None
        or resource_school_id is None
        or resource_year_id is None
        or authorized_school_id != resource_school_id
        or authorized_year_id != resource_year_id
    ):
        raise ScopeMismatchError("resource is outside the authorized school/year scope")


def ensure_revision(*, expected_revision: int, current_revision: int) -> None:
    """Require a non-negative, exact revision match for every mutation."""
    if expected_revision < 0 or current_revision < 0 or expected_revision != current_revision:
        raise RevisionConflictError("academic-year revision conflict")


def validate_school_timezone(value: str) -> str:
    """Validate an explicit IANA timezone without supplying a hidden default."""
    timezone_name = value.strip()
    if not timezone_name:
        raise InvalidTimezoneError("school timezone must be configured")
    try:
        ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise InvalidTimezoneError("school timezone must be a valid IANA timezone") from exc
    return timezone_name
