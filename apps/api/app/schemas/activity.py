from __future__ import annotations

from pydantic import BaseModel

from app.schemas.analytics import SeriesPoint, SummaryOut


class SectorOut(BaseModel):
    code: str
    name_fr: str
    name_ar: str | None
    latest_value: float | None
    latest_share_pct: float | None
    children: list[str]
    year: int | None = None
    source: str = "ANSADE/CN"
    unit: str = "Millions de MRU"


class SectorDetail(BaseModel):
    code: str
    name_fr: str
    name_ar: str | None
    unit: str
    series: list[SeriesPoint]
    contribution_series: list[SeriesPoint]
    summary: SummaryOut
    children: list[str]
    parent_code: str | None
    parent_contribution_series: list[SeriesPoint] = []
    cagr_pct: float | None = None
    completeness_score_pct: float = 0.0
    missing_years: list[int] = []
    anomalies: list[dict] = []
    source: str = "ANSADE/CN"


class MiningBranch(BaseModel):
    code: str
    name_fr: str
    name_ar: str | None
    latest_value: float | None
    share_of_parent_pct: float | None
    series: list[SeriesPoint] = []
    summary: SummaryOut | None = None
    anomalies: list[dict] = []


class MiningOverview(BaseModel):
    year: int | None
    extractive_activities_value: float | None
    extractive_share_of_gdp_pct: float | None
    oil_gas_share_of_extractive_pct: float | None
    metallic_share_of_extractive_pct: float | None = None
    snim_share_of_metallic_pct: float | None = None
    gold_copper_share_of_metallic_pct: float | None = None
    branches: list[MiningBranch]
    extractive_series: list[SeriesPoint] = []
    source: str = "ANSADE/CN"
    unit: str = "Millions de MRU"
    warnings: list[str] = []
