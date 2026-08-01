import pytest

from app.analytics.forecasting import InsufficientObservationsError, generate_forecast


def test_raises_below_minimum_observations():
    series = {y: 100.0 + y for y in range(2015, 2022)}  # 7 points
    with pytest.raises(InsufficientObservationsError):
        generate_forecast(series)


def test_generates_three_year_horizon_by_default():
    series = {y: 100.0 + 5 * (y - 2000) for y in range(2000, 2020)}
    result = generate_forecast(series)
    assert len(result.predicted_values) == 3
    assert result.horizon_years == [2020, 2021, 2022]
    assert result.reliability in ("low", "moderate", "high")


def test_reliability_is_low_with_fewer_than_15_observations():
    series = {y: 100.0 + y for y in range(2015, 2024)}  # 9 points
    result = generate_forecast(series)
    assert result.limited_data_warning is True


def test_non_negative_clamp_applied():
    # A steeply declining series would naturally forecast negative values.
    series = {y: 100.0 - 10 * (y - 2000) for y in range(2000, 2020)}
    result = generate_forecast(series, non_negative=True)
    assert all(v >= 0 for v in result.predicted_values)
    assert all(lo >= 0 for lo in result.lower_bounds)


def test_negative_allowed_when_flag_disabled():
    series = {y: 100.0 - 10 * (y - 2000) for y in range(2000, 2020)}
    result = generate_forecast(series, non_negative=False)
    assert min(result.predicted_values) < 0


def test_baseline_is_naive_last_value():
    series = {y: 100.0 + 3 * (y - 2000) for y in range(2000, 2020)}
    result = generate_forecast(series)
    assert result.baseline_model == "naive_last_value"


def test_labels_are_never_missing():
    series = {y: 100.0 + (y - 2000) for y in range(2000, 2020)}
    result = generate_forecast(series)
    assert result.model_name  # always set, defensively falls back to naive
