from app.analytics.anomalies import detect_anomalies


def test_too_short_series_returns_no_anomalies():
    assert detect_anomalies({2020: 100.0, 2021: 105.0}) == []


def test_single_sharp_outlier_is_flagged():
    series = {y: 100.0 + (y - 2010) for y in range(2010, 2024)}  # gentle +1/year trend
    series[2020] = series[2019] * 3  # sharp, isolated spike
    results = detect_anomalies(series)
    flagged_years = {r.year for r in results}
    assert 2020 in flagged_years
    spike = next(r for r in results if r.year == 2020)
    assert spike.severity in ("yellow", "orange", "red")


def test_not_every_max_is_flagged():
    # A gently, consistently rising series has its maximum at the last
    # point, but that point follows the same trend as every other year and
    # must not be flagged just for being the series maximum.
    series = {y: 100.0 + 2 * (y - 2000) for y in range(2000, 2020)}
    results = detect_anomalies(series)
    max_year = max(series, key=lambda y: series[y])
    flagged_years = {r.year for r in results}
    assert max_year not in flagged_years
