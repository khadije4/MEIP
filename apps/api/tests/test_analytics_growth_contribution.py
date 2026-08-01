import pytest

from app.analytics.contribution import contribution_change, contribution_series, rank_by_value, safe_share
from app.analytics.growth import annual_growth_series, cagr, summarize, volatility


def test_annual_growth_basic():
    series = {2020: 100.0, 2021: 110.0, 2022: 99.0}
    growth = annual_growth_series(series)
    assert growth[2021] == pytest.approx(10.0)
    assert growth[2022] == pytest.approx(-10.0)
    assert 2020 not in growth or growth[2020] is None


def test_annual_growth_missing_previous_year_is_none_not_skipped():
    series = {2020: 100.0, 2022: 120.0}  # 2021 missing
    growth = annual_growth_series(series)
    assert growth[2022] is None


def test_annual_growth_zero_previous_is_none_not_crash():
    series = {2020: 0.0, 2021: 50.0}
    growth = annual_growth_series(series)
    assert growth[2021] is None


def test_cagr_basic():
    series = {2018: 100.0, 2023: 200.0}
    result = cagr(series)
    expected = ((200.0 / 100.0) ** (1 / 5) - 1) * 100
    assert result == pytest.approx(expected)


def test_cagr_single_point_is_none():
    assert cagr({2020: 100.0}) is None


def test_cagr_zero_first_value_is_none():
    assert cagr({2020: 0.0, 2021: 50.0}) is None


def test_volatility_needs_at_least_two_growth_points():
    assert volatility({2020: None}) is None
    assert volatility({2020: 5.0, 2021: None}) is None
    assert volatility({2020: 5.0, 2021: 10.0}) is not None


def test_summarize_empty_series():
    summary = summarize({})
    assert summary.observation_count == 0
    assert summary.latest_value is None


def test_summarize_real_shape():
    series = {2020: 100.0, 2021: 90.0, 2022: 150.0, 2023: 140.0}
    summary = summarize(series)
    assert summary.latest_year == 2023
    assert summary.latest_value == 140.0
    assert summary.min_year == 2021
    assert summary.max_year == 2022
    assert summary.total_change == pytest.approx(40.0)
    assert summary.largest_increase_year == 2022  # (150-90)/90 = +66.7%


def test_safe_share_zero_denominator():
    assert safe_share(50.0, 0.0) is None


def test_safe_share_missing_values():
    assert safe_share(None, 100.0) is None
    assert safe_share(50.0, None) is None


def test_contribution_series_and_change():
    part = {2020: 20.0, 2021: 30.0}
    whole = {2020: 100.0, 2021: 100.0}
    contrib = contribution_series(part, whole)
    assert contrib[2020] == pytest.approx(20.0)
    assert contrib[2021] == pytest.approx(30.0)
    assert contribution_change(contrib, 2020, 2021) == pytest.approx(10.0)


def test_rank_by_value_excludes_none():
    ranked = rank_by_value({"a": 10.0, "b": None, "c": 30.0})
    assert ranked == [("c", 30.0), ("a", 10.0)]
