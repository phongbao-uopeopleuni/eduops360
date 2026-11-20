from statistics import median


def histogram(values: list[float], bin_count: int) -> list[int]:
    if not values:
        return [0] * bin_count
    if bin_count < 1:
        raise ValueError("BIN_COUNT_REQUIRED")
    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        return [len(values)] + [0] * (bin_count - 1)
    width = (maximum - minimum) / bin_count
    bins = [0] * bin_count
    for value in values:
        index = min(int((value - minimum) / width), bin_count - 1)
        bins[index] += 1
    return bins


def quartiles(values: list[float]) -> tuple[float, float, float]:
    if not values:
        raise ValueError("NO_VALUES")
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
    return q1, q2, q3
