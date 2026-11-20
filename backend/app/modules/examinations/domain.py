"""Policy-versioned assessment rules. Values are synthetic, not legal policy."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum


class GradeStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    LOCKED = "locked"


GRADE_TRANSITIONS = frozenset(
    {
        (GradeStatus.DRAFT, GradeStatus.SUBMITTED),
        (GradeStatus.SUBMITTED, GradeStatus.REVIEWED),
        (GradeStatus.REVIEWED, GradeStatus.APPROVED),
        (GradeStatus.APPROVED, GradeStatus.LOCKED),
    }
)


@dataclass(frozen=True)
class NumericPolicy:
    policy_id: str
    grade_min: float
    grade_max: float
    decimal_places: int


def validate_transition(current: GradeStatus, target: GradeStatus) -> str | None:
    if (current, target) not in GRADE_TRANSITIONS:
        return f"INVALID_TRANSITION:{current}:{target}"
    return None


def calculate_numeric_score(
    raw_score: float, policy: NumericPolicy
) -> tuple[float | None, str | None]:
    if raw_score < policy.grade_min or raw_score > policy.grade_max:
        return None, "OUT_OF_RANGE"
    if policy.decimal_places < 0 or policy.decimal_places > 3:
        return None, "INVALID_POLICY"
    quantum = Decimal("1").scaleb(-policy.decimal_places)
    rounded = Decimal(str(raw_score)).quantize(quantum, rounding=ROUND_HALF_UP)
    return float(rounded), None


def replay_policy_score(raw_score: float, policy: NumericPolicy) -> tuple[float | None, str | None]:
    return calculate_numeric_score(raw_score, policy)
