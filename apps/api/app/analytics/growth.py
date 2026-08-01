"""Pure growth/summary calculations over a sparse {year: value} series.

Series are never densified with 0 for missing years — a gap is simply
absent from the dict, and every function here treats missing years and
division-by-zero explicitly rather than crashing or guessing.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field


def annual_growth_series(series: dict[int, float]) -> dict[int, float | None]:
    """year -> ((value[year] - value[year-1]) / abs(value[year-1])) * 100.

    A year is present in the result only if the current year's value is
    known. The growth is None (not 0, not skipped) when the prior year is
    missing or is exactly zero (division-by-zero guarded)."""
    result: dict[int, float | None] = {}
    for year, value in series.items():
        prev = series.get(year - 1)
        if prev is None or prev == 0:
            result[year] = None
        else:
            result[year] = ((value - prev) / abs(prev)) * 100
    return result


def cagr(series: dict[int, float]) -> float | None:
    if len(series) < 2:
        return None
    years = sorted(series)
    first_year, last_year = years[0], years[-1]
    first_value, last_value = series[first_year], series[last_year]
    n_years = last_year - first_year
    if n_years <= 0 or first_value == 0 or (first_value < 0) != (last_value < 0):
        return None
    if first_value < 0:
        return None
    return ((last_value / first_value) ** (1 / n_years) - 1) * 100


def volatility(growth_series: dict[int, float | None]) -> float | None:
    values = [v for v in growth_series.values() if v is not None]
    if len(values) < 2:
        return None
    return statistics.stdev(values)


@dataclass
class SeriesSummary:
    latest_year: int | None = None
    latest_value: float | None = None
    min_year: int | None = None
    min_value: float | None = None
    max_year: int | None = None
    max_value: float | None = None
    average: float | None = None
    median: float | None = None
    total_change: float | None = None
    total_pct_change: float | None = None
    largest_increase_year: int | None = None
    largest_increase_pct: float | None = None
    largest_decrease_year: int | None = None
    largest_decrease_pct: float | None = None
    volatility: float | None = None
    observation_count: int = 0


def summarize(series: dict[int, float]) -> SeriesSummary:
    summary = SeriesSummary(observation_count=len(series))
    if not series:
        return summary

    years = sorted(series)
    summary.latest_year = years[-1]
    summary.latest_value = series[years[-1]]

    min_year = min(years, key=lambda y: series[y])
    max_year = max(years, key=lambda y: series[y])
    summary.min_year, summary.min_value = min_year, series[min_year]
    summary.max_year, summary.max_value = max_year, series[max_year]

    values = list(series.values())
    summary.average = statistics.mean(values)
    summary.median = statistics.median(values)

    first_year, last_year = years[0], years[-1]
    first_value, last_value = series[first_year], series[last_year]
    summary.total_change = last_value - first_value
    summary.total_pct_change = (
        ((last_value - first_value) / abs(first_value)) * 100 if first_value != 0 else None
    )

    growth = annual_growth_series(series)
    valid_growth = {y: g for y, g in growth.items() if g is not None}
    if valid_growth:
        inc_year = max(valid_growth, key=lambda y: valid_growth[y])
        dec_year = min(valid_growth, key=lambda y: valid_growth[y])
        summary.largest_increase_year, summary.largest_increase_pct = inc_year, valid_growth[inc_year]
        summary.largest_decrease_year, summary.largest_decrease_pct = dec_year, valid_growth[dec_year]

    summary.volatility = volatility(growth)
    return summary
