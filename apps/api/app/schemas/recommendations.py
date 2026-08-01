from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.stress_test import ShockRequest

Duration = Literal["temporary", "one_year", "multi_year"]
Horizon = Literal["immediate", "stabilization", "recovery", "structural"]
Priority = Literal["low", "medium", "high", "critical"]

class RecommendationGenerateRequest(BaseModel):
    year: int = Field(ge=1998, le=2024)
    shocks: list[ShockRequest] = Field(min_length=1)
    shock_duration: Duration = "temporary"
    objective: str | None = None
    budget_level: str | None = None
    implementation_horizon: str | None = None

class RecommendationItem(BaseModel):
    code: str
    title_fr: str
    title_ar: str
    description_fr: str
    description_ar: str
    time_horizon: Horizon
    priority: Priority
    sector_codes: list[str]
    reason_fr: str
    reason_ar: str
    supporting_metrics: list[str]
    monitoring_indicators: list[str]
    expected_objective_fr: str
    expected_objective_ar: str
    confidence: Literal["low", "moderate", "high"]
    limitations_fr: str
    limitations_ar: str

class AlternativeSector(BaseModel):
    indicator_code: str
    name_fr: str
    name_ar: str | None
    gdp_share_pct: float
    historical_growth_pct: float | None
    recent_growth_pct: float | None
    volatility_pct: float | None
    reason_fr: str
    reason_ar: str
    confidence: Literal["low", "moderate", "high"]
    limitation_fr: str
    limitation_ar: str

class RecommendationResponse(BaseModel):
    year: int
    risk_level: Literal["low", "moderate", "high", "critical"]
    risk_basis_fr: str
    risk_basis_ar: str
    stress_test: dict
    recommendations: list[RecommendationItem]
    alternative_sectors: list[AlternativeSector]
    monitoring_indicators: list[str]
    disclaimer_fr: str
    disclaimer_ar: str
    thresholds_disclaimer_fr: str
    thresholds_disclaimer_ar: str
    source: str
    unit: str

class CatalogueEntry(BaseModel):
    sector_code: str
    recommendations: list[RecommendationItem]
    monitoring_indicators: list[str]

