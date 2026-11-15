from datetime import date
from uuid import uuid4

import pytest

from app.modules.academic_years.domain import (
    ACADEMIC_TERM_TRANSITIONS,
    ACADEMIC_YEAR_TRANSITIONS,
    AcademicTermStatus,
    AcademicYearStatus,
    ActiveYearConflictError,
    ArchivedYearReadOnlyError,
    DateWindow,
    InvalidDateRangeError,
    InvalidStateTransitionError,
    InvalidTimezoneError,
    ParentYearStateError,
    RevisionConflictError,
    ScopeMismatchError,
    TermOutsideYearError,
    ensure_academic_term_transition,
    ensure_academic_year_transition,
    ensure_can_activate_academic_year,
    ensure_revision,
    ensure_year_mutable,
    ensure_year_scope,
    validate_school_timezone,
    validate_term_window,
)


def test_date_window_requires_start_before_end() -> None:
    with pytest.raises(InvalidDateRangeError):
        DateWindow(date(2026, 9, 1), date(2026, 9, 1))

    with pytest.raises(InvalidDateRangeError):
        DateWindow(date(2027, 5, 31), date(2026, 9, 1))


def test_term_window_must_be_fully_contained_in_year() -> None:
    year = DateWindow(date(2026, 9, 1), date(2027, 5, 31))
    term = DateWindow(date(2026, 9, 1), date(2027, 1, 15))

    validate_term_window(term=term, academic_year=year)

    with pytest.raises(TermOutsideYearError):
        validate_term_window(
            term=DateWindow(date(2026, 8, 31), date(2027, 1, 15)),
            academic_year=year,
        )

    with pytest.raises(TermOutsideYearError):
        validate_term_window(
            term=DateWindow(date(2027, 1, 16), date(2027, 6, 1)),
            academic_year=year,
        )


def test_year_transition_table_is_minimal_and_forward_only() -> None:
    assert ACADEMIC_YEAR_TRANSITIONS == frozenset(
        {
            (AcademicYearStatus.DRAFT, AcademicYearStatus.ACTIVE),
            (AcademicYearStatus.ACTIVE, AcademicYearStatus.ARCHIVED),
        }
    )

    ensure_academic_year_transition(AcademicYearStatus.DRAFT, AcademicYearStatus.ACTIVE)
    ensure_academic_year_transition(AcademicYearStatus.ACTIVE, AcademicYearStatus.ARCHIVED)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (AcademicYearStatus.DRAFT, AcademicYearStatus.DRAFT),
        (AcademicYearStatus.DRAFT, AcademicYearStatus.ARCHIVED),
        (AcademicYearStatus.ACTIVE, AcademicYearStatus.DRAFT),
        (AcademicYearStatus.ARCHIVED, AcademicYearStatus.ACTIVE),
    ],
)
def test_year_transition_rejects_noop_skip_and_reverse(
    current: AcademicYearStatus, target: AcademicYearStatus
) -> None:
    with pytest.raises(InvalidStateTransitionError):
        ensure_academic_year_transition(current, target)


def test_term_transition_requires_active_parent_year() -> None:
    assert ACADEMIC_TERM_TRANSITIONS == frozenset(
        {
            (AcademicTermStatus.DRAFT, AcademicTermStatus.ACTIVE),
            (AcademicTermStatus.ACTIVE, AcademicTermStatus.ARCHIVED),
        }
    )

    with pytest.raises(ParentYearStateError):
        ensure_academic_term_transition(
            AcademicTermStatus.DRAFT,
            AcademicTermStatus.ACTIVE,
            parent_year_status=AcademicYearStatus.DRAFT,
        )

    ensure_academic_term_transition(
        AcademicTermStatus.DRAFT,
        AcademicTermStatus.ACTIVE,
        parent_year_status=AcademicYearStatus.ACTIVE,
    )


def test_term_cannot_change_after_parent_year_is_archived() -> None:
    with pytest.raises(ArchivedYearReadOnlyError):
        ensure_academic_term_transition(
            AcademicTermStatus.ACTIVE,
            AcademicTermStatus.ARCHIVED,
            parent_year_status=AcademicYearStatus.ARCHIVED,
        )


def test_term_transition_rejects_reverse_and_noop() -> None:
    with pytest.raises(InvalidStateTransitionError):
        ensure_academic_term_transition(
            AcademicTermStatus.ACTIVE,
            AcademicTermStatus.DRAFT,
            parent_year_status=AcademicYearStatus.ACTIVE,
        )

    with pytest.raises(InvalidStateTransitionError):
        ensure_academic_term_transition(
            AcademicTermStatus.DRAFT,
            AcademicTermStatus.DRAFT,
            parent_year_status=AcademicYearStatus.ACTIVE,
        )


def test_only_one_different_active_year_is_allowed_per_school() -> None:
    candidate_year_id = uuid4()

    ensure_can_activate_academic_year(candidate_year_id, active_year_id=None)
    ensure_can_activate_academic_year(candidate_year_id, active_year_id=candidate_year_id)

    with pytest.raises(ActiveYearConflictError):
        ensure_can_activate_academic_year(candidate_year_id, active_year_id=uuid4())


def test_archived_year_is_read_only() -> None:
    ensure_year_mutable(AcademicYearStatus.DRAFT)
    ensure_year_mutable(AcademicYearStatus.ACTIVE)

    with pytest.raises(ArchivedYearReadOnlyError):
        ensure_year_mutable(AcademicYearStatus.ARCHIVED)


def test_year_scope_requires_exact_school_and_year_match() -> None:
    school_id = uuid4()
    year_id = uuid4()

    ensure_year_scope(
        authorized_school_id=school_id,
        authorized_year_id=year_id,
        resource_school_id=school_id,
        resource_year_id=year_id,
    )

    with pytest.raises(ScopeMismatchError):
        ensure_year_scope(
            authorized_school_id=school_id,
            authorized_year_id=year_id,
            resource_school_id=uuid4(),
            resource_year_id=year_id,
        )

    with pytest.raises(ScopeMismatchError):
        ensure_year_scope(
            authorized_school_id=school_id,
            authorized_year_id=year_id,
            resource_school_id=school_id,
            resource_year_id=uuid4(),
        )

    with pytest.raises(ScopeMismatchError):
        ensure_year_scope(
            authorized_school_id=None,
            authorized_year_id=None,
            resource_school_id=school_id,
            resource_year_id=year_id,
        )


def test_revision_mismatch_fails_instead_of_last_write_wins() -> None:
    ensure_revision(expected_revision=3, current_revision=3)

    with pytest.raises(RevisionConflictError):
        ensure_revision(expected_revision=2, current_revision=3)

    with pytest.raises(RevisionConflictError):
        ensure_revision(expected_revision=-1, current_revision=0)


def test_school_timezone_must_be_explicit_and_valid() -> None:
    assert validate_school_timezone("Asia/Ho_Chi_Minh") == "Asia/Ho_Chi_Minh"
    assert validate_school_timezone("UTC") == "UTC"

    with pytest.raises(InvalidTimezoneError):
        validate_school_timezone("")

    with pytest.raises(InvalidTimezoneError):
        validate_school_timezone("Asia/Not_A_Real_Zone")
