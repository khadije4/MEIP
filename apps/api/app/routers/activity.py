from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analytics.contribution import contribution_series, safe_share
from app.analytics.anomalies import detect_anomalies
from app.analytics.growth import cagr, summarize
from app.analytics.ratios import (oil_gas_share_of_extractive, extractive_dependence,
    snim_share_of_metallic, gold_copper_share_of_metallic)
from app.database import get_db
from app.models.indicator import Indicator
from app.schemas.activity import MiningBranch, MiningOverview, SectorDetail, SectorOut
from app.schemas.analytics import SeriesPoint, SummaryOut
from app.services.series import get_indicator_or_404, get_ok_series

router = APIRouter(prefix="/api/activity", tags=["activity"])

_TOP_SECTORS = ["primary_sector", "secondary_sector", "tertiary_sector"]
_MINING_BRANCHES = [
    "oil_gas_extraction", "non_oil_extractive_activities", "metallic_mineral_extraction",
    "snim_iron", "gold_copper", "other_extractive_activities",
]


def _alerts(series: dict[int, float]) -> list[dict]:
    return [a.__dict__ for a in detect_anomalies(series)]


@router.get("/sectors", response_model=list[SectorOut])
def list_sectors(year: int | None = Query(default=None, ge=1900, le=2100), db: Session = Depends(get_db)) -> list[SectorOut]:
    gdp_series = get_ok_series(db, "gdp_activity_market_prices")
    latest_year = year if year is not None else (max(gdp_series) if gdp_series else None)
    if year is not None and year not in gdp_series:
        raise HTTPException(status_code=400, detail={"code": "year_not_available", "message_en": f"Year {year} is not available.", "message_fr": f"L'annee {year} n'est pas disponible.", "message_ar": "السنة المطلوبة غير متاحة."})

    results = []
    for code in _TOP_SECTORS:
        ind = get_indicator_or_404(db, code)
        series = get_ok_series(db, code)
        children = [c.code for c in db.query(Indicator).filter(Indicator.parent_indicator_id == ind.id).all()]
        latest_value = series.get(latest_year) if latest_year else None
        share = safe_share(latest_value, gdp_series.get(latest_year)) if latest_year else None
        results.append(
            SectorOut(
                code=ind.code, name_fr=ind.name_fr, name_ar=ind.name_ar,
                latest_value=latest_value, latest_share_pct=share, children=children,
                year=latest_year, unit=ind.unit,
            )
        )
    return results


@router.get("/sectors/{code}", response_model=SectorDetail)
def get_sector_detail(code: str, db: Session = Depends(get_db)) -> SectorDetail:
    ind = get_indicator_or_404(db, code)
    series = get_ok_series(db, code)
    gdp_series = get_ok_series(db, "gdp_activity_market_prices")
    contribution = contribution_series(series, gdp_series)
    children = [c.code for c in db.query(Indicator).filter(Indicator.parent_indicator_id == ind.id).all()]
    parent_code = None
    if ind.parent_indicator_id:
        parent = db.query(Indicator).filter(Indicator.id == ind.parent_indicator_id).first()
        parent_code = parent.code if parent else None
    parent_contribution = contribution_series(series, get_ok_series(db, parent_code)) if parent_code else {}
    years = sorted(series)
    missing_years = list(range(years[0], years[-1] + 1)) if years else []
    missing_years = [y for y in missing_years if y not in series]
    expected = (years[-1] - years[0] + 1) if years else 0

    return SectorDetail(
        code=ind.code, name_fr=ind.name_fr, name_ar=ind.name_ar, unit=ind.unit,
        series=[SeriesPoint(year=y, value=v) for y, v in sorted(series.items())],
        contribution_series=[SeriesPoint(year=y, value=v) for y, v in sorted(contribution.items())],
        summary=SummaryOut(**summarize(series).__dict__),
        children=children, parent_code=parent_code,
        parent_contribution_series=[SeriesPoint(year=y, value=v) for y, v in sorted(parent_contribution.items())],
        cagr_pct=cagr(series), completeness_score_pct=(len(series) / expected * 100 if expected else 0),
        missing_years=missing_years, anomalies=_alerts(series),
    )


@router.get("/mining", response_model=MiningOverview)
def mining_overview(db: Session = Depends(get_db)) -> MiningOverview:
    extractive_series = get_ok_series(db, "extractive_activities")
    gdp_series = get_ok_series(db, "gdp_activity_market_prices")
    metallic_series = get_ok_series(db, "metallic_mineral_extraction")
    year = max(extractive_series) if extractive_series else None

    branches = []
    for code in _MINING_BRANCHES:
        ind = get_indicator_or_404(db, code)
        series = get_ok_series(db, code)
        value = series.get(year) if year else None
        parent_value = (
            metallic_series.get(year)
            if code in ("snim_iron", "gold_copper")
            else extractive_series.get(year)
        )
        share = safe_share(value, parent_value)
        branches.append(
            MiningBranch(code=ind.code, name_fr=ind.name_fr, name_ar=ind.name_ar,
                          latest_value=value, share_of_parent_pct=share, series=[SeriesPoint(year=y, value=v) for y, v in sorted(series.items())],
                          summary=SummaryOut(**summarize(series).__dict__), anomalies=_alerts(series))
        )

    oil = get_ok_series(db, "oil_gas_extraction")
    snim = get_ok_series(db, "snim_iron")
    gold = get_ok_series(db, "gold_copper")
    warnings = []
    if year is not None and year not in oil:
        warnings.append("Petroleum/gas value is not available for the latest year; it was not treated as zero.")

    return MiningOverview(
        year=year,
        extractive_activities_value=extractive_series.get(year) if year else None,
        extractive_share_of_gdp_pct=extractive_dependence(
            extractive_series.get(year) if year else None, gdp_series.get(year) if year else None
        ),
        oil_gas_share_of_extractive_pct=oil_gas_share_of_extractive(
            oil.get(year) if year else None,
            extractive_series.get(year) if year else None,
        ),
        metallic_share_of_extractive_pct=safe_share(metallic_series.get(year) if year else None, extractive_series.get(year) if year else None),
        snim_share_of_metallic_pct=snim_share_of_metallic(snim.get(year) if year else None, metallic_series.get(year) if year else None),
        gold_copper_share_of_metallic_pct=gold_copper_share_of_metallic(gold.get(year) if year else None, metallic_series.get(year) if year else None),
        branches=branches,
        extractive_series=[SeriesPoint(year=y, value=v) for y, v in sorted(extractive_series.items())], warnings=warnings,
    )
