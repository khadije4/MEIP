from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ShockRequest(BaseModel):
    indicator_code: str
    shock_rate: float = Field(ge=0, le=1)


class SingleShockRequest(ShockRequest):
    year: int = Field(ge=1998, le=2024)


class MultipleShockRequest(BaseModel):
    year: int = Field(ge=1998, le=2024)
    shocks: list[ShockRequest] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_codes(self):
        codes = [shock.indicator_code for shock in self.shocks]
        if len(codes) != len(set(codes)):
            raise ValueError("Each indicator may appear only once.")
        return self


class SectorEffect(BaseModel):
    indicator_code: str
    name_fr: str
    name_ar: str | None
    sector_value: float
    sector_share_of_gdp_pct: float
    shock_rate: float
    direct_loss: float
    simulated_gdp: float
    direct_gdp_impact_pct: float


class SingleShockResponse(SectorEffect):
    year: int
    baseline_activity_gdp: float
    current_price_warning_fr: str
    current_price_warning_ar: str
    source: str
    unit: str
    methodology_disclaimer_fr: str
    methodology_disclaimer_ar: str


class MultipleShockResponse(BaseModel):
    year: int
    baseline_activity_gdp: float
    individual_effects: list[SectorEffect]
    total_direct_loss: float
    total_direct_gdp_impact_pct: float
    simulated_gdp: float
    hierarchy_validation: Literal["valid"] = "valid"
    warnings_fr: list[str]
    warnings_ar: list[str]
    source: str
    unit: str
    methodology_disclaimer_fr: str
    methodology_disclaimer_ar: str


class DependencyPoint(BaseModel):
    year: int
    sector_value: float
    activity_gdp: float
    dependency_pct: float
    nominal_growth_contribution_pct: float | None = None


class DependencyResponse(BaseModel):
    indicator_code: str
    name_fr: str
    name_ar: str | None
    start_year: int
    end_year: int
    points: list[DependencyPoint]
    minimum_dependency_pct: float | None
    minimum_year: int | None
    maximum_dependency_pct: float | None
    maximum_year: int | None
    latest_dependency_pct: float | None
    average_dependency_pct: float | None
    trend: str
    missing_years: list[int]
    warnings_fr: list[str]
    warnings_ar: list[str]
    source: str
    unit: str


class RankingItem(BaseModel):
    indicator_code: str
    name_fr: str
    name_ar: str | None
    economic_value: float
    gdp_share_pct: float
    latest_annual_growth_pct: float | None
    historical_average_growth_pct: float | None
    volatility_pct: float | None
    shutdown_impact_pct: float
    largest_historical_gdp_share_pct: float | None
    smallest_historical_gdp_share_pct: float | None
    completeness_pct: float
    vulnerability_rank: int


class RankingResponse(BaseModel):
    year: int
    ranking_group: str
    sectors: list[RankingItem]
    source: str
    unit: str
    warning_fr: str
    warning_ar: str


class ConcentrationSector(BaseModel):
    indicator_code: str
    name_fr: str
    name_ar: str | None
    economic_value: float
    share_of_activity_gdp_pct: float


class ConcentrationResponse(BaseModel):
    year: int
    ranking_group: str
    hhi: float
    included_sectors: list[ConcentrationSector]
    interpretation: str
    methodology_warning_fr: str
    methodology_warning_ar: str
    source: str
    unit: str


class PresetScenario(BaseModel):
    code: str
    title_fr: str
    title_ar: str
    shocks: list[ShockRequest]

