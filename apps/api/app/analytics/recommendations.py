"""Pure deterministic rules for experimental response recommendations."""

from __future__ import annotations

from typing import Literal

Risk = Literal["low", "moderate", "high", "critical"]

RISK_ORDER = {"low": 0, "moderate": 1, "high": 2, "critical": 3}
DURATION_SCORE = {"temporary": 0, "one_year": 1, "multi_year": 2}


def base_risk(direct_impact_pct: float) -> Risk:
    if direct_impact_pct < 2: return "low"
    if direct_impact_pct < 5: return "moderate"
    if direct_impact_pct < 10: return "high"
    return "critical"


def classify_risk(
    direct_impact_pct: float, *, volatility_pct: float | None = None,
    largest_sector_share_pct: float | None = None, largest_shock_rate: float = 0,
    duration: str = "temporary", combined_shocks: int = 1,
    concentration_hhi: float | None = None, recent_negative_growth: bool = False,
) -> Risk:
    """Classify risk, allowing corroborating vulnerabilities to raise it one level."""
    risk = base_risk(direct_impact_pct)
    flags = sum((
        volatility_pct is not None and volatility_pct >= 15,
        largest_sector_share_pct is not None and largest_sector_share_pct >= 15,
        largest_shock_rate >= 0.75,
        DURATION_SCORE.get(duration, 0) >= 1,
        combined_shocks > 1,
        concentration_hhi is not None and concentration_hhi >= 0.25,
        recent_negative_growth,
    ))
    if flags >= 3 and risk != "critical":
        return list(RISK_ORDER)[RISK_ORDER[risk] + 1]  # type: ignore[return-value]
    return risk


def confidence_from_completeness(completeness_pct: float | None) -> str:
    if completeness_pct is None or completeness_pct < 70: return "low"
    if completeness_pct < 90: return "moderate"
    return "high"


def alternative_score(*, historical_growth_pct: float | None, volatility_pct: float | None,
                      recent_growth_pct: float | None, completeness_pct: float,
                      gdp_share_pct: float) -> float:
    """Balanced score; growth alone can never dominate selection."""
    growth = max(-20, min(20, historical_growth_pct or 0)) / 20
    recent = max(-20, min(20, recent_growth_pct or 0)) / 20
    stability = 1 - min(1, (volatility_pct or 50) / 50)
    completeness = completeness_pct / 100
    scale = min(1, gdp_share_pct / 20)
    return 0.2 * growth + 0.1 * recent + 0.25 * stability + 0.25 * completeness + 0.2 * scale

