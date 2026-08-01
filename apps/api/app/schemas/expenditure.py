from __future__ import annotations

from pydantic import BaseModel

from app.schemas.analytics import SeriesPoint, SummaryOut


class ExpenditureOverview(BaseModel):
    gdp_series: list[SeriesPoint]
    final_consumption_series: list[SeriesPoint]
    gross_fixed_capital_formation_series: list[SeriesPoint]
    inventory_changes_series: list[SeriesPoint]
    exports_series: list[SeriesPoint]
    imports_series: list[SeriesPoint]
    latest_year: int | None
    consumption_rate_pct: float | None
    investment_rate_pct: float | None
    trade_balance: float | None = None
    export_ratio_pct: float | None = None
    import_ratio_pct: float | None = None
    trade_openness_pct: float | None = None
    source: str = "ANSADE/CN"
    unit: str = "Millions de MRU"


class TradeOverview(BaseModel):
    exports_series: list[SeriesPoint]
    imports_series: list[SeriesPoint]
    trade_balance_series: list[SeriesPoint]
    export_ratio_series: list[SeriesPoint]
    import_ratio_series: list[SeriesPoint]
    trade_openness_series: list[SeriesPoint]
    exports_growth_series: list[SeriesPoint] = []
    imports_growth_series: list[SeriesPoint] = []
    maximum_balance_year: int | None = None
    maximum_balance: float | None = None
    largest_deficit_year: int | None = None
    largest_deficit: float | None = None
    anomalies: dict[str, list[dict]] = {}
    source: str = "ANSADE/CN"
    unit: str = "Millions de MRU"


class ConsumptionOverview(BaseModel):
    final_consumption_series: list[SeriesPoint]
    household_final_consumption_series: list[SeriesPoint]
    household_market_consumption_series: list[SeriesPoint]
    household_nonmarket_consumption_series: list[SeriesPoint]
    government_final_consumption_series: list[SeriesPoint]
    isblm_final_consumption_series: list[SeriesPoint]
    consumption_rate_series: list[SeriesPoint]
    component_share_series: dict[str, list[SeriesPoint]] = {}
    summaries: dict[str, SummaryOut] = {}
    source: str = "ANSADE/CN"
    unit: str = "Millions de MRU"


class InvestmentOverview(BaseModel):
    gross_fixed_capital_formation_series: list[SeriesPoint]
    inventory_changes_series: list[SeriesPoint]
    net_acquisition_valuables_series: list[SeriesPoint]
    investment_rate_series: list[SeriesPoint]
    summaries: dict[str, SummaryOut] = {}
    missing_years: list[int] = []
    warnings: list[str] = []
    source: str = "ANSADE/CN"
    unit: str = "Millions de MRU"
