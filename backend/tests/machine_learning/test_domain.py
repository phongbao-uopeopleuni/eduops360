from datetime import date

from app.modules.machine_learning.domain import (
    FeatureSnapshot,
    mae,
    mean_baseline,
    validate_as_of_snapshot,
)


def test_as_of_rejects_future_features_and_empty_snapshots():
    prediction_date = date(2026, 11, 20)
    future = FeatureSnapshot("synthetic-1", date(2026, 11, 21), {"score": 7.0})
    empty = FeatureSnapshot("synthetic-1", date(2026, 11, 20), {})
    assert validate_as_of_snapshot(future, prediction_date) == "FUTURE_FEATURE"
    assert validate_as_of_snapshot(empty, prediction_date) == "EMPTY_FEATURES"
    assert (
        validate_as_of_snapshot(
            FeatureSnapshot("synthetic-1", date(2026, 11, 20), {"score": 7.0}),
            prediction_date,
        )
        is None
    )


def test_mean_baseline_and_mae_are_servable_only_for_matching_series():
    assert mean_baseline([1.0, 2.0, 3.0]) == 2.0
    assert mae([1.0, 2.0, 3.0], [1.5, 1.5, 3.5]) == 0.5
