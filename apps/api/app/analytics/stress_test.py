"""Pure accounting calculations for sector stress testing.

The functions in this module receive plain values/series.  They never query
the database and never fill missing observations with zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean, pstdev


@dataclass(frozen=True)
class ShockInput:
    indicator_code: str
    sector_value: float
    shock_rate: float


def validate_shock_rate(shock_rate: float) -> None:
    if not 0 <= shock_rate <= 1:
        raise ValueError("shock_rate must be between 0 and 1")


def simulate_single_sector_shock(
    year: int,
    indicator_code: str,
    shock_rate: float,
    *,
    sector_value: float,
    baseline_activity_gdp: float,
) -> dict[str, float | int | str]:
    """Calculate the direct accounting effect of one sector decline."""
    validate_shock_rate(shock_rate)
    if baseline_activity_gdp == 0:
        raise ValueError("baseline activity GDP cannot be zero")
    direct_loss = sector_value * shock_rate
    return {
        "year": year,
        "indicator_code": indicator_code,
        "sector_value": sector_value,
        "sector_share_of_gdp_pct": sector_value / baseline_activity_gdp * 100,
        "shock_rate": shock_rate,
        "direct_loss": direct_loss,
        "simulated_gdp": baseline_activity_gdp - direct_loss,
        "direct_gdp_impact_pct": direct_loss / baseline_activity_gdp * 100,
    }


def simulate_multi_sector_shock(
    year: int,
    shocks: list[ShockInput],
    *,
    baseline_activity_gdp: float,
) -> dict:
    effects = [
        simulate_single_sector_shock(
            year,
            shock.indicator_code,
            shock.shock_rate,
            sector_value=shock.sector_value,
            baseline_activity_gdp=baseline_activity_gdp,
        )
        for shock in shocks
    ]
    total_loss = sum(float(effect["direct_loss"]) for effect in effects)
    return {
        "year": year,
        "baseline_activity_gdp": baseline_activity_gdp,
        "individual_effects": effects,
        "total_direct_loss": total_loss,
        "simulated_gdp": baseline_activity_gdp - total_loss,
        "total_direct_gdp_impact_pct": total_loss / baseline_activity_gdp * 100,
    }


def growth_rates(series: dict[int, float]) -> dict[int, float]:
    rates: dict[int, float] = {}
    for year in sorted(series):
        previous = series.get(year - 1)
        if previous is not None and previous != 0:
            rates[year] = (series[year] - previous) / previous * 100
    return rates


def sector_growth_contribution(
    sector_series: dict[int, float], activity_gdp_series: dict[int, float]
) -> dict[int, float]:
    """Accounting contribution to nominal GDP change, in percentage points."""
    result: dict[int, float] = {}
    for year, value in sector_series.items():
        previous_sector = sector_series.get(year - 1)
        previous_gdp = activity_gdp_series.get(year - 1)
        if previous_sector is not None and previous_gdp not in (None, 0):
            result[year] = (value - previous_sector) / previous_gdp * 100
    return result


def dependency_series(
    sector_series: dict[int, float],
    activity_gdp_series: dict[int, float],
    start_year: int,
    end_year: int,
) -> tuple[dict[int, float], list[int]]:
    dependency: dict[int, float] = {}
    missing: list[int] = []
    for year in range(start_year, end_year + 1):
        sector = sector_series.get(year)
        gdp = activity_gdp_series.get(year)
        if sector is None or gdp in (None, 0):
            missing.append(year)
        else:
            dependency[year] = sector / gdp * 100
    return dependency, missing


def trend_label(series: dict[int, float]) -> str:
    if len(series) < 2:
        return "insufficient_data"
    years = sorted(series)
    change = series[years[-1]] - series[years[0]]
    if abs(change) < 0.1:
        return "stable"
    return "increasing" if change > 0 else "decreasing"


def calculate_concentration(values: dict[str, float], activity_gdp: float) -> dict:
    if activity_gdp == 0:
        raise ValueError("baseline activity GDP cannot be zero")
    shares = {code: value / activity_gdp for code, value in values.items()}
    hhi = sum(share**2 for share in shares.values())
    interpretation = (
        "relatively_diversified" if hhi < 0.15 else
        "moderately_concentrated" if hhi < 0.25 else
        "highly_concentrated"
    )
    return {"hhi": hhi, "shares": shares, "interpretation": interpretation}


def vulnerability_metrics(
    sector_series: dict[int, float], activity_gdp_series: dict[int, float], year: int
) -> dict:
    value = sector_series[year]
    gdp = activity_gdp_series[year]
    rates = growth_rates(sector_series)
    dependencies = {
        y: sector_series[y] / activity_gdp_series[y] * 100
        for y in sector_series.keys() & activity_gdp_series.keys()
        if activity_gdp_series[y] != 0
    }
    expected = max(sector_series) - min(sector_series) + 1 if sector_series else 0
    return {
        "economic_value": value,
        "gdp_share_pct": value / gdp * 100,
        "latest_annual_growth_pct": rates.get(year),
        "historical_average_growth_pct": mean(rates.values()) if rates else None,
        "volatility_pct": pstdev(rates.values()) if len(rates) > 1 else None,
        "shutdown_impact_pct": value / gdp * 100,
        "largest_historical_gdp_share_pct": max(dependencies.values()) if dependencies else None,
        "smallest_historical_gdp_share_pct": min(dependencies.values()) if dependencies else None,
        "completeness_pct": len(sector_series) / expected * 100 if expected else 0,
    }

