from datetime import date, time

import pytest

from app.modules.school_calendar.domain import (
    intervals_overlap,
    validate_holiday_range,
    validate_slot_collection,
    validate_slot_interval,
)


def test_zero_duration_and_reverse_interval_are_rejected():
    assert validate_slot_interval(time(8, 0), time(8, 0)) == "ZERO_DURATION"
    assert validate_slot_interval(time(9, 0), time(8, 0)) == "INVALID_INTERVAL"
    assert validate_slot_interval(time(0, 0), time(0, 45)) is None


def test_adjacent_intervals_do_not_overlap_but_crossing_intervals_do():
    assert not intervals_overlap(time(8, 0), time(8, 45), time(8, 45), time(9, 30))
    assert intervals_overlap(time(8, 0), time(9, 0), time(8, 30), time(9, 30))


def test_slot_collection_rejects_duplicate_overlap_in_sorted_window():
    assert (
        validate_slot_collection(
            [
                ("Tiết 1", time(8, 0), time(8, 45)),
                ("Tiết 2", time(8, 30), time(9, 15)),
            ]
        )
        == "Tiết 1_Tiết 2:OVERLAP"
    )


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (date(2026, 9, 1), date(2026, 9, 1)),
        (date(2026, 9, 1), date(2026, 9, 5)),
        (date(2027, 5, 31), date(2027, 5, 31)),
    ],
)
def test_valid_holiday_ranges_allow_single_or_multi_day_dates(start, end):
    assert (
        validate_holiday_range(
            start,
            end,
            year_start=date(2026, 9, 1),
            year_end=date(2027, 5, 31),
        )
        is None
    )


def test_holiday_range_rejects_reverse_outside_and_missing_boundaries():
    assert (
        validate_holiday_range(
            date(2026, 9, 5),
            date(2026, 9, 1),
            year_start=date(2026, 9, 1),
            year_end=date(2027, 5, 31),
        )
        == "INVALID_RANGE"
    )
    assert (
        validate_holiday_range(
            date(2026, 8, 31),
            date(2026, 9, 1),
            year_start=date(2026, 9, 1),
            year_end=date(2027, 5, 31),
        )
        == "OUTSIDE_ACADEMIC_YEAR"
    )
