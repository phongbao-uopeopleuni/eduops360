"""Fail-closed chart input values without query or rendering behavior."""

from dataclasses import dataclass
from uuid import UUID


class ChartInputError(ValueError):
    """Base error for invalid chart input."""


class UnknownVariableError(ChartInputError):
    """Raised when a variable has not been reviewed for analytics use."""


class InappropriateVariableError(ChartInputError):
    """Raised for direct PII/identifiers or a variable in an unsuitable role."""


class MutableChartInputError(TypeError):
    """Raised when a chart input collection is mutable."""


APPROVED_VARIABLES = frozenset(
    {
        "assessment_value",
        "grade_level",
        "class_code",
        "gender",
        "academic_year",
        "subject",
    }
)

BLOCKED_DIRECT_VARIABLES = frozenset(
    {
        "student_id",
        "student_code",
        "full_name",
        "date_of_birth",
        "email",
        "phone",
    }
)

ROLE_VARIABLES = {
    "x": APPROVED_VARIABLES,
    "y": frozenset({"assessment_value", "grade_level"}),
    "group": frozenset({"grade_level", "class_code", "gender", "academic_year", "subject"}),
    "filter": frozenset({"grade_level", "class_code", "gender", "academic_year", "subject"}),
}


def _validate_variable(name: str, *, role: str) -> None:
    if name in BLOCKED_DIRECT_VARIABLES:
        raise InappropriateVariableError(f"{name} is a direct identifier or PII field")
    if name not in APPROVED_VARIABLES:
        raise UnknownVariableError(f"{name} is not in the reviewed analytics catalog")
    if name not in ROLE_VARIABLES[role]:
        raise InappropriateVariableError(f"{name} is not appropriate for chart role {role}")


@dataclass(frozen=True, slots=True)
class ChartFilter:
    field: str
    values: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.values, tuple):
            raise MutableChartInputError("filter values must be an immutable tuple")
        if not self.values:
            raise ChartInputError("filter values cannot be empty")
        _validate_variable(self.field, role="filter")


@dataclass(frozen=True, slots=True)
class ChartInput:
    """A reviewed variable selection scoped to one academic year."""

    academic_year_id: UUID
    subject_id: UUID | None
    x: str
    y: str | None = None
    group_by: str | None = None
    filters: tuple[ChartFilter, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.filters, tuple):
            raise MutableChartInputError("filters must be an immutable tuple")
        _validate_variable(self.x, role="x")
        if self.y is not None:
            _validate_variable(self.y, role="y")
        if self.group_by is not None:
            _validate_variable(self.group_by, role="group")
