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
