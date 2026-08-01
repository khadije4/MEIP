from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analytics.anomalies import detect_anomalies
from app.analytics.contribution import safe_share
from app.analytics.growth import annual_growth_series, summarize
from app.analytics.ratios import trade_balance
from app.database import get_db
from app.models.indicator import Indicator
from app.models.reconciliation import ReconciliationIssue
from app.schemas.dashboard import DashboardOverview, DashboardYearSnapshot, YearSnapshotIndicator
from app.services.series import get_ok_series

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_SECTOR_CODES = ["primary_sector", "secondary_sector", "tertiary_sector"]
_ACTIVITY_BRANCH_CODES = [
    "agriculture_forestry", "livestock_hunting", "fishing", "extractive_activities",
    "oil_gas_extraction", "non_oil_extractive_activities", "metallic_mineral_extraction",
    "snim_iron", "gold_copper", "other_extractive_activities", "manufacturing",
    "manufacturing_excluding_water_electricity", "water_electricity", "construction_public_works",
    "transport_information_communication", "transport", "information_communication", "commerce",
    "other_services", "public_administration",
]
_PRICE_NOTE_FR = (
    "Toutes les valeurs sont à prix courants (nominaux) ; l'évolution reflète donc la "
    "croissance nominale, pas la croissance réelle corrigée de l'inflation."
)
_PRICE_NOTE_AR = (
    "جميع القيم بالأسعار الجارية (الاسمية)؛ لذا فإن التطور يعكس النمو الاسمي وليس النمو "
    "الحقيقي المعدل حسب التضخم."
)


@router.get("/overview", response_model=DashboardOverview)
def dashboard_overview(db: Session = Depends(get_db)) -> DashboardOverview:
    gdp_activity_series = get_ok_series(db, "gdp_activity_market_prices")
    gdp_expenditure_series = get_ok_series(db, "gdp_expenditure")
    exports_series = get_ok_series(db, "exports")
    imports_series = get_ok_series(db, "imports")

    if not gdp_activity_series:
        return DashboardOverview(
            latest_year=None, latest_gdp_activity=None, latest_gdp_expenditure=None,
            gdp_activity_growth_pct=None, largest_sector_code=None, largest_sector_name_fr=None,
            largest_sector_share_pct=None, fastest_growing_branch_code=None,
            fastest_growing_branch_name_fr=None, fastest_growing_branch_growth_pct=None,
            most_volatile_branch_code=None, most_volatile_branch_name_fr=None,
            most_volatile_branch_volatility=None, latest_trade_balance=None, alert_count=0,
            completeness_score=0.0, unit="Unit not confirmed",
            price_type_note_fr=_PRICE_NOTE_FR, price_type_note_ar=_PRICE_NOTE_AR,
        )

    latest_year = max(gdp_activity_series)
    growth = annual_growth_series(gdp_activity_series)

    largest_code, largest_share = None, None
    for code in _SECTOR_CODES:
        series = get_ok_series(db, code)
        value = series.get(latest_year)
        share = safe_share(value, gdp_activity_series.get(latest_year))
        if share is not None and (largest_share is None or share > largest_share):
            largest_code, largest_share = code, share

    fastest_code, fastest_growth = None, None
    most_volatile_code, most_volatile_value = None, None
    for code in _ACTIVITY_BRANCH_CODES:
        series = get_ok_series(db, code)
        if not series:
            continue
        g = annual_growth_series(series).get(latest_year)
        if g is not None and (fastest_growth is None or g > fastest_growth):
            fastest_code, fastest_growth = code, g
        summary = summarize(series)
        if summary.volatility is not None and (
            most_volatile_value is None or summary.volatility > most_volatile_value
        ):
            most_volatile_code, most_volatile_value = code, summary.volatility

    def _name(code: str | None) -> str | None:
        if code is None:
            return None
        ind = db.query(Indicator).filter(Indicator.code == code).first()
        return ind.name_fr if ind else None

    alert_count = 0
    for code in _SECTOR_CODES + _ACTIVITY_BRANCH_CODES + ["gdp_activity_market_prices", "gdp_expenditure"]:
        alert_count += len(
            detect_anomalies(get_ok_series(db, code), include_isolation_forest=False)
        )

    from app.routers.data import data_quality

    quality_rows = data_quality(db)
    completeness = (
        sum(q.completeness_score for q in quality_rows) / len(quality_rows) if quality_rows else 0.0
    )

    return DashboardOverview(
        latest_year=latest_year,
        latest_gdp_activity=gdp_activity_series.get(latest_year),
        latest_gdp_expenditure=gdp_expenditure_series.get(latest_year),
        gdp_activity_growth_pct=growth.get(latest_year),
        largest_sector_code=largest_code,
        largest_sector_name_fr=_name(largest_code),
        largest_sector_share_pct=largest_share,
        fastest_growing_branch_code=fastest_code,
        fastest_growing_branch_name_fr=_name(fastest_code),
        fastest_growing_branch_growth_pct=fastest_growth,
        most_volatile_branch_code=most_volatile_code,
        most_volatile_branch_name_fr=_name(most_volatile_code),
        most_volatile_branch_volatility=most_volatile_value,
        latest_trade_balance=trade_balance(exports_series.get(latest_year), imports_series.get(latest_year)),
        alert_count=alert_count,
        completeness_score=round(completeness, 2),
        unit="Millions de MRU",
        price_type_note_fr=_PRICE_NOTE_FR,
        price_type_note_ar=_PRICE_NOTE_AR,
    )


@router.get("/year/{year}", response_model=DashboardYearSnapshot)
def dashboard_year(year: int, db: Session = Depends(get_db)) -> DashboardYearSnapshot:
    gdp_activity_series = get_ok_series(db, "gdp_activity_market_prices")
    gdp_expenditure_series = get_ok_series(db, "gdp_expenditure")
    exports_series = get_ok_series(db, "exports")
    imports_series = get_ok_series(db, "imports")

    if year not in gdp_activity_series and year not in gdp_expenditure_series:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "year_not_available",
                "message_en": f"No data available for year {year}.",
                "message_ar": f"لا توجد بيانات متاحة لسنة {year}.",
                "message_fr": f"Aucune donnée disponible pour l'année {year}.",
            },
        )

    sectors = []
    for code in _SECTOR_CODES:
        series = get_ok_series(db, code)
        ind = db.query(Indicator).filter(Indicator.code == code).first()
        growth = annual_growth_series(series).get(year)
        share = safe_share(series.get(year), gdp_activity_series.get(year))
        sectors.append(
            YearSnapshotIndicator(
                code=code, name_fr=ind.name_fr, name_ar=ind.name_ar,
                value=series.get(year), growth_pct=growth, share_of_gdp_activity_pct=share,
            )
        )

    issue = (
        db.query(ReconciliationIssue).filter(ReconciliationIssue.year == year).first()
    )

    return DashboardYearSnapshot(
        year=year,
        gdp_activity=gdp_activity_series.get(year),
        gdp_expenditure=gdp_expenditure_series.get(year),
        trade_balance=trade_balance(exports_series.get(year), imports_series.get(year)),
        sectors=sectors,
        reconciliation_absolute_difference=issue.absolute_difference if issue else None,
        reconciliation_percentage_difference=issue.percentage_difference if issue else None,
    )
