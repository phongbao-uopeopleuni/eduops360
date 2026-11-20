import pytest

from app.modules.examinations.domain import (
    GradeStatus,
    NumericPolicy,
    calculate_numeric_score,
    replay_policy_score,
    validate_transition,
)


def test_grade_state_requires_forward_sequence():
    assert validate_transition(GradeStatus.DRAFT, GradeStatus.SUBMITTED) is None
    assert validate_transition(GradeStatus.APPROVED, GradeStatus.LOCKED) is None
    assert validate_transition(GradeStatus.LOCKED, GradeStatus.DRAFT) is not None


@pytest.mark.parametrize(("score", "expected"), [(7.0, 7.0), (7.25, 7.3), (10.0, 10.0)])
def test_numeric_policy_rounding_and_bounds(score, expected):
    policy = NumericPolicy("synthetic-v1", 0.0, 10.0, 1)
    value, error = calculate_numeric_score(score, policy)
    assert error is None
    assert value == expected


def test_out_of_range_is_rejected_and_policy_history_is_replayable():
    policy = NumericPolicy("synthetic-v1", 0.0, 10.0, 1)
    assert calculate_numeric_score(-1.0, policy) == (None, "OUT_OF_RANGE")
    assert replay_policy_score(8.26, policy) == (8.3, None)
