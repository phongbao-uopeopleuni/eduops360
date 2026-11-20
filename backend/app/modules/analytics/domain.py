from math import isfinite
from statistics import median


def histogram(values: list[float], bin_count: int) -> list[int]:
    if bin_count < 1:
        raise ValueError("BIN_COUNT_REQUIRED")
    if any(not isfinite(value) for value in values):
        raise ValueError("NON_FINITE_VALUE")
    if not values:
        return [0] * bin_count
    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        return [len(values)] + [0] * (bin_count - 1)
    value_range = maximum - minimum
    if not isfinite(value_range) or value_range <= 0:
        raise ValueError("NON_FINITE_RANGE")
    width = value_range / bin_count
    if not isfinite(width) or width <= 0:
        raise ValueError("NON_FINITE_WIDTH")
    bins = [0] * bin_count
    for value in values:
        index = min(int((value - minimum) / width), bin_count - 1)
        bins[index] += 1
    return bins


def quartiles(values: list[float]) -> tuple[float, float, float]:
    if not values:
        raise ValueError("NO_VALUES")
    if any(not isfinite(value) for value in values):
        raise ValueError("NON_FINITE_VALUE")
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        lower = ordered[:midpoint]
        upper = ordered[midpoint + 1 :]
        q2 = ordered[midpoint]
    else:
        lower = ordered[:midpoint]
        upper = ordered[midpoint:]
        q2 = median(ordered)
    q1 = median(lower)
    q3 = median(upper)
    if any(not isfinite(value) for value in (q1, q2, q3)):
        raise ValueError("NON_FINITE_VALUE")
    return q1, q2, q3
