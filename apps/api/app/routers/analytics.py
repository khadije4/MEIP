from __future__ import annotations

import statistics

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analytics.anomalies import detect_anomalies
from app.analytics.contribution import contribution_series
from app.analytics.growth import annual_growth_series, summarize
from app.database import get_db
from app.schemas.analytics import (
    AnomalyOut,
    AnomalyResponse,
    CompareIndicatorSeries,
    CompareResponse,
    ContributionPoint,
    ContributionResponse,
    GrowthPoint,
    GrowthResponse,
    SeriesPoint,
    SummaryOut,
)
from app.services.series import get_indicator_or_404, get_ok_series

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/growth", response_model=GrowthResponse)
def analytics_growth(indicator: str = Query(...), db: Session = Depends(get_db)) -> GrowthResponse:
    ind = get_indicator_or_404(db, indicator)
    series = get_ok_series(db, indicator)
    growth = annual_growth_series(series)
    summary = summarize(series)

    points = [
        GrowthPoint(year=year, value=series[year], growth_pct=growth.get(year))
        for year in sorted(series)
    ]
    return GrowthResponse(
        indicator_code=ind.code,
        name_fr=ind.name_fr,
        name_ar=ind.name_ar,
        unit=ind.unit,
        source_side=ind.source_side,
        points=points,
        summary=SummaryOut(**summary.__dict__),
    )


@router.get("/contribution", response_model=ContributionResponse)
def analytics_contribution(
    part: str = Query(...), whole: str = Query(...), db: Session = Depends(get_db)
) -> ContributionResponse:
    part_ind = get_indicator_or_404(db, part)
    whole_ind = get_indicator_or_404(db, whole)
    part_series = get_ok_series(db, part)
    whole_series = get_ok_series(db, whole)
    contrib = contribution_series(part_series, whole_series)

    points = [
        ContributionPoint(
            year=year,
            part_value=part_series.get(year),
            whole_value=whole_series.get(year),
            share_pct=contrib.get(year),
        )
        for year in sorted(contrib)
    ]
    return ContributionResponse(
        part_code=part_ind.code, part_name_fr=part_ind.name_fr,
        whole_code=whole_ind.code, whole_name_fr=whole_ind.name_fr,
        points=points,
    )


@router.get("/compare", response_model=CompareResponse)
def analytics_compare(
    first: str = Query(...),
    second: str = Query(...),
    start_year: int | None = None,
    end_year: int | None = None,
    db: Session = Depends(get_db),
) -> CompareResponse:
    first_ind = get_indicator_or_404(db, first)
    second_ind = get_indicator_or_404(db, second)
    first_series = get_ok_series(db, first)
    second_series = get_ok_series(db, second)

    def _filter(series: dict[int, float]) -> dict[int, float]:
        return {
            y: v for y, v in series.items()
            if (start_year is None or y >= start_year) and (end_year is None or y <= end_year)
        }

    first_series, second_series = _filter(first_series), _filter(second_series)
    common_years = sorted(set(first_series) & set(second_series))

    def _build(series: dict[int, float], ind) -> CompareIndicatorSeries:
        years = sorted(series)
        base_year = years[0] if years else None
        base_value = series.get(base_year) if base_year is not None else None
        indexed = [
            SeriesPoint(
                year=y,
                value=(series[y] / base_value * 100) if base_value not in (None, 0) else None,
            )
            for y in years
        ]
        growth = annual_growth_series(series)
        return CompareIndicatorSeries(
            code=ind.code, name_fr=ind.name_fr, name_ar=ind.name_ar, unit=ind.unit,
            absolute=[SeriesPoint(year=y, value=series[y]) for y in years],
            indexed=indexed,
            growth=[GrowthPoint(year=y, value=series[y], growth_pct=growth.get(y)) for y in years],
        )

    correlation: float | None = None
    if len(common_years) >= 3:
        try:
            correlation = statistics.correlation(
                [first_series[y] for y in common_years], [second_series[y] for y in common_years]
            )
        except statistics.StatisticsError:
            correlation = None

    note_fr = (
        "Une corrélation, même élevée, ne démontre pas de lien de causalité entre les deux indicateurs."
    )
    note_ar = "الارتباط، حتى لو كان مرتفعًا، لا يثبت وجود علاقة سببية بين المؤشرين."

    return CompareResponse(
        first=_build(first_series, first_ind),
        second=_build(second_series, second_ind),
        correlation=correlation,
        common_years=common_years,
        note_fr=note_fr,
        note_ar=note_ar,
    )


def _anomaly_explanations(name_fr: str, name_ar: str | None, unit: str, a) -> tuple[str, str]:
    fr = (
        f"En {a.year}, {name_fr} est passé de {a.previous_value:,.2f} à {a.observed_value:,.2f} "
        f"{unit} ({a.percentage_change:+.2f} %), un écart jugé inhabituel par rapport à la "
        f"variation médiane ({a.median_growth:+.2f} %) — z robuste = {a.robust_z_score:.2f}."
    )
    ar = (
        f"في سنة {a.year}، تغيّر {name_ar or name_fr} من {a.previous_value:,.2f} إلى "
        f"{a.observed_value:,.2f} {unit} ({a.percentage_change:+.2f}%)، وهو تغير غير معتاد "
        f"مقارنة بالتغير الوسيط ({a.median_growth:+.2f}%) — القيمة المعيارية القوية = "
        f"{a.robust_z_score:.2f}."
    )
    return fr, ar


@router.get("/anomalies", response_model=AnomalyResponse)
def analytics_anomalies(indicator: str = Query(...), db: Session = Depends(get_db)) -> AnomalyResponse:
    ind = get_indicator_or_404(db, indicator)
    series = get_ok_series(db, indicator)
    anomalies = detect_anomalies(series)

    alerts = []
    for a in anomalies:
        explanation_fr, explanation_ar = _anomaly_explanations(ind.name_fr, ind.name_ar, ind.unit, a)
        alerts.append(
            AnomalyOut(
                year=a.year,
                observed_value=a.observed_value,
                previous_value=a.previous_value,
                percentage_change=a.percentage_change,
                median_growth=a.median_growth,
                mad=a.mad,
                robust_z_score=a.robust_z_score,
                severity=a.severity,
                isolation_forest_flagged=a.isolation_forest_flagged,
                explanation_fr=explanation_fr,
                explanation_ar=explanation_ar,
            )
        )

    return AnomalyResponse(indicator_code=ind.code, name_fr=ind.name_fr, name_ar=ind.name_ar, alerts=alerts)
