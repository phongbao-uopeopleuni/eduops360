"""Pure temporal rules for school calendars."""

from datetime import date, time


def validate_slot_interval(
    start_time: time,
    end_time: time,
) -> str | None:
    if start_time is None or end_time is None:
        return "NULL_TIME"
    if start_time == end_time:
        return "ZERO_DURATION"
    if end_time < start_time:
        return "INVALID_INTERVAL"
    return None


def intervals_overlap(
    start_a: time,
    end_a: time,
    start_b: time,
    end_b: time,
) -> bool:
    return start_a < end_b and start_b < end_a


def validate_slot_collection(
    slots: list[tuple[str, time, time]],
) -> str | None:
    for label, start, end in slots:
        error = validate_slot_interval(start, end)
        if error:
            return f"{label}:{error}"

    ordered = sorted(slots, key=lambda item: item[1])
    for previous, current in zip(ordered, ordered[1:], strict=False):
        if intervals_overlap(previous[1], previous[2], current[1], current[2]):
            return f"{previous[0]}_{current[0]}:OVERLAP"
    return None


def validate_holiday_range(
    start_date: date,
    end_date: date,
    *,
    year_start: date,
    year_end: date,
) -> str | None:
    if start_date is None or end_date is None:
        return "NULL_DATE"
    if end_date < start_date:
        return "INVALID_RANGE"
    if start_date < year_start or end_date > year_end:
        return "OUTSIDE_ACADEMIC_YEAR"
    return None
