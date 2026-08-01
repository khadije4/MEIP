"""Transparent anomaly detection on year-over-year growth: median, median
absolute deviation (MAD), and a robust Z-score, with an optional Isolation
Forest cross-check. Not every max/min is flagged — only growth years whose
robust Z-score clears a minimum threshold are returned.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from app.analytics.growth import annual_growth_series

_SEVERITY_THRESHOLDS = (
    (1.5, None),     # below this: not anomalous, not returned
    (2.5, "yellow"),
    (3.5, "orange"),
)
_RED = "red"


@dataclass
class AnomalyResult:
    year: int
    observed_value: float
    previous_value: float
    percentage_change: float
    median_growth: float
    mad: float
    robust_z_score: float
    severity: str
    isolation_forest_flagged: bool | None


def _severity_for_z(abs_z: float) -> str | None:
    if abs_z < _SEVERITY_THRESHOLDS[0][0]:
        return None
    if abs_z < _SEVERITY_THRESHOLDS[1][0]:
        return _SEVERITY_THRESHOLDS[1][1]
    if abs_z < _SEVERITY_THRESHOLDS[2][0]:
        return _SEVERITY_THRESHOLDS[2][1]
    return _RED


def _isolation_forest_flags(growth_values: list[float]) -> dict[int, bool] | None:
    """Optional secondary signal. Requires at least 6 points to be
    meaningful; returns None (i.e. "not run") otherwise."""
    if len(growth_values) < 6:
        return None
    try:
        from sklearn.ensemble import IsolationForest
    except ImportError:
        return None

    import numpy as np

    X = np.array(growth_values).reshape(-1, 1)
    model = IsolationForest(contamination="auto", random_state=42)
    predictions = model.fit_predict(X)
    # Cast numpy.bool_ to the built-in bool so API responses remain JSON serializable.
    return {i: bool(pred == -1) for i, pred in enumerate(predictions)}


def detect_anomalies(
    series: dict[int, float], *, include_isolation_forest: bool = True
) -> list[AnomalyResult]:
    """Detect robust-Z anomalies.

    Isolation Forest is an optional secondary annotation and never controls
    whether an alert is returned. Callers that only need an alert count can
    disable it to avoid fitting a model for every series.
    """
    growth = annual_growth_series(series)
    valid_years = sorted(y for y, g in growth.items() if g is not None)
    if len(valid_years) < 3:
        return []

    growth_values = [growth[y] for y in valid_years]
    median_growth = statistics.median(growth_values)
    abs_deviations = [abs(g - median_growth) for g in growth_values]
    mad = statistics.median(abs_deviations)

    iso_flags = _isolation_forest_flags(growth_values) if include_isolation_forest else None

    results: list[AnomalyResult] = []
    for idx, year in enumerate(valid_years):
        g = growth_values[idx]
        if mad == 0:
            # No spread to compare against; fall back to exact-equality
            # check so a single outlier amid flat data still surfaces.
            z = 0.0 if g == median_growth else float("inf")
        else:
            z = 0.6745 * (g - median_growth) / mad
        severity = _severity_for_z(abs(z))
        if severity is None:
            continue

        results.append(
            AnomalyResult(
                year=year,
                observed_value=series[year],
                previous_value=series[year - 1],
                percentage_change=g,
                median_growth=median_growth,
                mad=mad,
                robust_z_score=z,
                severity=severity,
                isolation_forest_flagged=iso_flags.get(idx) if iso_flags else None,
            )
        )
    return results
