import pytest

from app.modules.analytics.domain import histogram, quartiles


def test_histogram_bins_known_values():
    assert histogram([1.0, 2.0, 3.0, 4.0], 2) == [2, 2]
    assert histogram([5.0, 5.0], 4) == [2, 0, 0, 0]


def test_quartiles_match_known_reference():
    assert quartiles([1.0, 2.0, 3.0, 4.0]) == (1.5, 2.5, 3.5)


def test_empty_or_invalid_bins_fail_explicitly():
    assert histogram([], 3) == [0, 0, 0]
    with pytest.raises(ValueError):
        histogram([1.0], 0)
    with pytest.raises(ValueError):
        quartiles([])


def test_histogram_rejects_zero_bins_before_empty_values_and_non_finite():
    with pytest.raises(ValueError, match="BIN_COUNT_REQUIRED"):
        histogram([], 0)
    with pytest.raises(ValueError, match="NON_FINITE_VALUE"):
        histogram([float("inf")], 2)


def test_quartiles_reject_non_finite_and_extreme_histogram_range():
    with pytest.raises(ValueError, match="NON_FINITE_VALUE"):
        quartiles([1.0, float("nan")])
    with pytest.raises(ValueError, match="NON_FINITE_RANGE"):
        histogram([-1e308, 1e308], 2)


def test_quartiles_reject_overflowing_median_output():
    with pytest.raises(ValueError, match="NON_FINITE_VALUE"):
        quartiles([1e308, 1e308, -1e308, -1e308])
