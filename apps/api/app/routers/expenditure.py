from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.anomalies import detect_anomalies
from app.analytics.contribution import safe_share
from app.analytics.growth import annual_growth_series, summarize
from app.analytics.ratios import (
    consumption_rate as consumption_rate_fn,
    export_ratio as export_ratio_fn,
    import_ratio as import_ratio_fn,
    investment_rate as investment_rate_fn,
    trade_balance as trade_balance_fn,
    trade_openness as trade_openness_fn,
)
from app.database import get_db
from app.schemas.analytics import SeriesPoint, SummaryOut
from app.schemas.expenditure import ConsumptionOverview, ExpenditureOverview, InvestmentOverview, TradeOverview
from app.services.series import get_ok_series

router = APIRouter(prefix="/api/expenditure", tags=["expenditure"])


def _points(series: dict[int, float]) -> list[SeriesPoint]:
    return [SeriesPoint(year=y, value=v) for y, v in sorted(series.items())]


def _ratio_series(numerator: dict[int, float], denominator: dict[int, float], fn) -> dict[int, float]:
    years = set(numerator) & set(denominator)
    result = {}
    for y in years:
        r = fn(numerator.get(y), denominator.get(y))
        if r is not None:
            result[y] = r
    return result


def _growth_points(series: dict[int, float]) -> list[SeriesPoint]:
    return [SeriesPoint(year=y, value=v) for y, v in sorted(annual_growth_series(series).items())]


def _summary(series: dict[int, float]) -> SummaryOut:
    return SummaryOut(**summarize(series).__dict__)


@router.get("/overview", response_model=ExpenditureOverview)
def expenditure_overview(db: Session = Depends(get_db)) -> ExpenditureOverview:
    gdp = get_ok_series(db, "gdp_expenditure")
    final_consumption = get_ok_series(db, "final_consumption")
    gfcf = get_ok_series(db, "gross_fixed_capital_formation")
    inventory = get_ok_series(db, "inventory_changes")
    exports = get_ok_series(db, "exports")
    imports = get_ok_series(db, "imports")

    latest_year = max(gdp) if gdp else None
    return ExpenditureOverview(
        gdp_series=_points(gdp),
        final_consumption_series=_points(final_consumption),
        gross_fixed_capital_formation_series=_points(gfcf),
        inventory_changes_series=_points(inventory),
        exports_series=_points(exports),
        imports_series=_points(imports),
        latest_year=latest_year,
        consumption_rate_pct=consumption_rate_fn(
            final_consumption.get(latest_year), gdp.get(latest_year)
        ) if latest_year else None,
        investment_rate_pct=investment_rate_fn(gfcf.get(latest_year), gdp.get(latest_year)) if latest_year else None,
        trade_balance=trade_balance_fn(exports.get(latest_year), imports.get(latest_year)) if latest_year else None,
        export_ratio_pct=export_ratio_fn(exports.get(latest_year), gdp.get(latest_year)) if latest_year else None,
        import_ratio_pct=import_ratio_fn(imports.get(latest_year), gdp.get(latest_year)) if latest_year else None,
        trade_openness_pct=trade_openness_fn(exports.get(latest_year), imports.get(latest_year), gdp.get(latest_year)) if latest_year else None,
    )


@router.get("/trade", response_model=TradeOverview)
def expenditure_trade(db: Session = Depends(get_db)) -> TradeOverview:
    exports = get_ok_series(db, "exports")
    imports = get_ok_series(db, "imports")
    gdp = get_ok_series(db, "gdp_expenditure")

    balance = {y: trade_balance_fn(exports.get(y), imports.get(y)) for y in set(exports) & set(imports)}
    valid_balance = {y: v for y, v in balance.items() if v is not None}
    max_year = max(valid_balance, key=valid_balance.get) if valid_balance else None
    deficit_year = min(valid_balance, key=valid_balance.get) if valid_balance else None
    return TradeOverview(
        exports_series=_points(exports),
        imports_series=_points(imports),
        trade_balance_series=_points(valid_balance),
        export_ratio_series=_points(_ratio_series(exports, gdp, export_ratio_fn)),
        import_ratio_series=_points(_ratio_series(imports, gdp, import_ratio_fn)),
        trade_openness_series=_points({
            y: trade_openness_fn(exports.get(y), imports.get(y), gdp.get(y))
            for y in set(exports) & set(imports) & set(gdp)
            if trade_openness_fn(exports.get(y), imports.get(y), gdp.get(y)) is not None
        }),
        exports_growth_series=_growth_points(exports), imports_growth_series=_growth_points(imports),
        maximum_balance_year=max_year, maximum_balance=valid_balance.get(max_year) if max_year else None,
        largest_deficit_year=deficit_year, largest_deficit=valid_balance.get(deficit_year) if deficit_year else None,
        anomalies={"exports": [a.__dict__ for a in detect_anomalies(exports)], "imports": [a.__dict__ for a in detect_anomalies(imports)]},
    )


@router.get("/consumption", response_model=ConsumptionOverview)
def expenditure_consumption(db: Session = Depends(get_db)) -> ConsumptionOverview:
    final_consumption = get_ok_series(db, "final_consumption")
    household = get_ok_series(db, "household_final_consumption")
    household_market = get_ok_series(db, "household_market_consumption")
    household_nonmarket = get_ok_series(db, "household_nonmarket_consumption")
    government = get_ok_series(db, "government_final_consumption")
    isblm = get_ok_series(db, "isblm_final_consumption")
    gdp = get_ok_series(db, "gdp_expenditure")

    return ConsumptionOverview(
        final_consumption_series=_points(final_consumption),
        household_final_consumption_series=_points(household),
        household_market_consumption_series=_points(household_market),
        household_nonmarket_consumption_series=_points(household_nonmarket),
        government_final_consumption_series=_points(government),
        isblm_final_consumption_series=_points(isblm),
        consumption_rate_series=_points(_ratio_series(final_consumption, gdp, consumption_rate_fn)),
        component_share_series={code: _points({y: share for y in set(values) & set(final_consumption) if (share := safe_share(values[y], final_consumption[y])) is not None}) for code, values in {
            "household_final_consumption": household, "household_market_consumption": household_market,
            "household_nonmarket_consumption": household_nonmarket, "government_final_consumption": government,
            "isblm_final_consumption": isblm}.items()},
        summaries={code: _summary(values) for code, values in {"final_consumption": final_consumption,
            "household_final_consumption": household, "household_market_consumption": household_market,
            "household_nonmarket_consumption": household_nonmarket, "government_final_consumption": government,
            "isblm_final_consumption": isblm}.items()},
    )


@router.get("/investment", response_model=InvestmentOverview)
def expenditure_investment(db: Session = Depends(get_db)) -> InvestmentOverview:
    gfcf = get_ok_series(db, "gross_fixed_capital_formation")
    inventory = get_ok_series(db, "inventory_changes")
    net_acquisition = get_ok_series(db, "net_acquisition_valuables")
    gdp = get_ok_series(db, "gdp_expenditure")
    all_years = sorted(gdp)
    missing_years = [y for y in all_years if y not in net_acquisition]
    warnings = (["Net acquisition of valuables is unavailable for years: " + ", ".join(map(str, missing_years)) + ". Missing values were not treated as zero."] if missing_years else [])

    return InvestmentOverview(
        gross_fixed_capital_formation_series=_points(gfcf),
        inventory_changes_series=_points(inventory),
        net_acquisition_valuables_series=_points(net_acquisition),
        investment_rate_series=_points(_ratio_series(gfcf, gdp, investment_rate_fn)),
        summaries={"gross_fixed_capital_formation": _summary(gfcf), "inventory_changes": _summary(inventory),
                   "net_acquisition_valuables": _summary(net_acquisition)},
        missing_years=missing_years, warnings=warnings,
    )
