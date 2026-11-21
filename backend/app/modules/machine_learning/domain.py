from dataclasses import dataclass
from datetime import date
from math import fsum, isfinite


@dataclass(frozen=True)
class FeatureSnapshot:
    student_id: str
    as_of: date
    features: dict[str, float]


def validate_as_of_snapshot(snapshot: FeatureSnapshot, prediction_date: date) -> str | None:
    if snapshot.as_of > prediction_date:
        return "FUTURE_FEATURE"
    if not snapshot.features:
        return "EMPTY_FEATURES"
    if any(not isfinite(value) for value in snapshot.features.values()):
        return "NON_FINITE_FEATURE"
    return None


def mean_baseline(actual: list[float]) -> float:
    if not actual:
        raise ValueError("NO_ACTUAL_VALUES")
    if any(not isfinite(value) for value in actual):
        raise ValueError("NON_FINITE_VALUE")
    try:
        value = fsum(actual) / len(actual)
    except OverflowError as exc:
        raise ValueError("NON_FINITE_VALUE") from exc
    if not isfinite(value):
        raise ValueError("NON_FINITE_VALUE")
    return value


def mae(actual: list[float], predicted: list[float]) -> float:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("INVALID_SERIES")
    if any(not isfinite(value) for value in actual + predicted):
        raise ValueError("NON_FINITE_VALUE")
    differences = [abs(a - p) for a, p in zip(actual, predicted, strict=True)]
    if any(not isfinite(value) for value in differences):
        raise ValueError("NON_FINITE_VALUE")
    try:
        value = fsum(differences) / len(actual)
    except OverflowError as exc:
        raise ValueError("NON_FINITE_VALUE") from exc
    if not isfinite(value):
        raise ValueError("NON_FINITE_VALUE")
    return value
