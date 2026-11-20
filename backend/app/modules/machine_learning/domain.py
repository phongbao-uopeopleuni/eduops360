from dataclasses import dataclass
from datetime import date


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
    return None


def mean_baseline(actual: list[float]) -> float:
    if not actual:
        raise ValueError("NO_ACTUAL_VALUES")
    return sum(actual) / len(actual)


def mae(actual: list[float], predicted: list[float]) -> float:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("INVALID_SERIES")
    return sum(abs(a - p) for a, p in zip(actual, predicted, strict=True)) / len(actual)
