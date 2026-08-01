"""Sector/subsector contribution-to-GDP calculations. Division-by-zero and
missing years are handled by returning None rather than raising or
guessing."""

from __future__ import annotations


def safe_share(part: float | None, whole: float | None) -> float | None:
    if part is None or whole is None or whole == 0:
        return None
    return (part / whole) * 100


def contribution_series(
    part_series: dict[int, float], whole_series: dict[int, float]
) -> dict[int, float | None]:
    years = set(part_series) | set(whole_series)
    return {
        year: safe_share(part_series.get(year), whole_series.get(year))
        for year in sorted(years)
    }


def contribution_change(
    contribution: dict[int, float | None], from_year: int, to_year: int
) -> float | None:
    start = contribution.get(from_year)
    end = contribution.get(to_year)
    if start is None or end is None:
        return None
    return end - start


def rank_by_value(values_by_code: dict[str, float | None]) -> list[tuple[str, float]]:
    """Descending rank of codes with a known (non-None) value for a given year."""
    known = [(code, v) for code, v in values_by_code.items() if v is not None]
    return sorted(known, key=lambda pair: pair[1], reverse=True)
