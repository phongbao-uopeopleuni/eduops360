from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.modules.analytics.chart_input import (
    ChartFilter,
    ChartInput,
    InappropriateVariableError,
    MutableChartInputError,
    UnknownVariableError,
)


def test_chart_input_keeps_year_subject_roles_and_filters() -> None:
    academic_year_id = uuid4()
    subject_id = uuid4()
    chart_input = ChartInput(
        academic_year_id=academic_year_id,
        subject_id=subject_id,
        x="grade_level",
        y="assessment_value",
        group_by="gender",
        filters=(ChartFilter(field="class_code", values=("8A1", "8A2")),),
    )

    assert chart_input.academic_year_id == academic_year_id
    assert chart_input.subject_id == subject_id
    assert chart_input.x == "grade_level"
    assert chart_input.y == "assessment_value"
    assert chart_input.group_by == "gender"
    assert chart_input.filters[0].values == ("8A1", "8A2")


@pytest.mark.parametrize(
    "field",
    ["student_id", "student_code", "full_name", "date_of_birth", "email", "phone"],
)
def test_direct_identifiers_and_pii_are_rejected(field: str) -> None:
    with pytest.raises(InappropriateVariableError):
        ChartInput(academic_year_id=uuid4(), subject_id=None, x=field)


def test_unknown_variable_fails_closed() -> None:
    with pytest.raises(UnknownVariableError):
        ChartInput(academic_year_id=uuid4(), subject_id=None, x="unreviewed_metric")


def test_role_inappropriate_variable_is_rejected() -> None:
    with pytest.raises(InappropriateVariableError):
        ChartInput(
            academic_year_id=uuid4(),
            subject_id=None,
            x="grade_level",
            group_by="assessment_value",
        )


def test_filter_rejects_pii_and_mutable_values() -> None:
    with pytest.raises(InappropriateVariableError):
        ChartFilter(field="full_name", values=("Synthetic Student",))

    with pytest.raises(MutableChartInputError):
        ChartFilter(field="class_code", values=["8A1"])  # type: ignore[arg-type]


def test_chart_input_is_immutable() -> None:
    chart_input = ChartInput(academic_year_id=uuid4(), subject_id=None, x="grade_level")

    with pytest.raises(FrozenInstanceError):
        chart_input.x = "subject"  # type: ignore[misc]
