from __future__ import annotations

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    latest_year: int | None
    latest_gdp_activity: float | None
    latest_gdp_expenditure: float | None
    gdp_activity_growth_pct: float | None
    largest_sector_code: str | None
    largest_sector_name_fr: str | None
    largest_sector_share_pct: float | None
    fastest_growing_branch_code: str | None
    fastest_growing_branch_name_fr: str | None
    fastest_growing_branch_growth_pct: float | None
    most_volatile_branch_code: str | None
    most_volatile_branch_name_fr: str | None
    most_volatile_branch_volatility: float | None
    latest_trade_balance: float | None
    alert_count: int
    completeness_score: float
    unit: str
    price_type_note_fr: str
    price_type_note_ar: str


class YearSnapshotIndicator(BaseModel):
    code: str
    name_fr: str
    name_ar: str | None
    value: float | None
    growth_pct: float | None
    share_of_gdp_activity_pct: float | None


class DashboardYearSnapshot(BaseModel):
    year: int
    gdp_activity: float | None
    gdp_expenditure: float | None
    trade_balance: float | None
    sectors: list[YearSnapshotIndicator]
    reconciliation_absolute_difference: float | None
    reconciliation_percentage_difference: float | None
