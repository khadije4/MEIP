from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class SeriesPoint(BaseModel):
    year: int
    value: float | None


class GrowthPoint(BaseModel):
    year: int
    value: float
    growth_pct: float | None


class SummaryOut(BaseModel):
    latest_year: int | None
    latest_value: float | None
    min_year: int | None
    min_value: float | None
    max_year: int | None
    max_value: float | None
    average: float | None
    median: float | None
    total_change: float | None
    total_pct_change: float | None
    largest_increase_year: int | None
    largest_increase_pct: float | None
    largest_decrease_year: int | None
    largest_decrease_pct: float | None
    volatility: float | None
    observation_count: int


class GrowthResponse(BaseModel):
    indicator_code: str
    name_fr: str
    name_ar: str | None
    unit: str
    source_side: str
    points: list[GrowthPoint]
    summary: SummaryOut


class ContributionPoint(BaseModel):
    year: int
    part_value: float | None
    whole_value: float | None
    share_pct: float | None


class ContributionResponse(BaseModel):
    part_code: str
    part_name_fr: str
    whole_code: str
    whole_name_fr: str
    points: list[ContributionPoint]


class CompareIndicatorSeries(BaseModel):
    code: str
    name_fr: str
    name_ar: str | None
    unit: str
    absolute: list[SeriesPoint]
    indexed: list[SeriesPoint]
    growth: list[GrowthPoint]


class CompareResponse(BaseModel):
    first: CompareIndicatorSeries
    second: CompareIndicatorSeries
    correlation: float | None
    common_years: list[int]
    note_fr: str
    note_ar: str


class AnomalyOut(BaseModel):
    year: int
    observed_value: float
    previous_value: float
    percentage_change: float
    median_growth: float
    mad: float
    robust_z_score: float
    severity: str
    isolation_forest_flagged: bool | None
    explanation_fr: str
    explanation_ar: str


class AnomalyResponse(BaseModel):
    indicator_code: str
    name_fr: str
    name_ar: str | None
    alerts: list[AnomalyOut]


class ForecastRequest(BaseModel):
    indicator_code: str
    horizon: int = Field(default=3, ge=1, le=3)
    horizon_years: int | None = Field(default=None, ge=1, le=3)
    start_year: int | None = None
    end_year: int | None = None
    preferred_model: str | None = None

    @model_validator(mode="after")
    def validate_period(self):
        if self.start_year is not None and self.end_year is not None and self.start_year > self.end_year:
            raise ValueError("start_year must be less than or equal to end_year")
        return self

    @property
    def requested_horizon(self) -> int:
        return self.horizon_years if self.horizon_years is not None else self.horizon


class ForecastResponseOut(BaseModel):
    indicator_code: str
    name_fr: str
    name_ar: str | None
    unit: str
    historical: list[SeriesPoint]
    model_name: str
    baseline_model: str
    horizon_years: list[int]
    predicted_values: list[float]
    lower_bounds: list[float]
    upper_bounds: list[float]
    mae: float | None
    mape: float | None
    baseline_mae: float | None
    baseline_mape: float | None
    reliability: str
    limited_data_warning: bool
    observation_count: int
    clamped_to_zero: bool
    disclaimer_fr: str
    disclaimer_ar: str
    historical_start_year: int | None = None
    historical_end_year: int | None = None
    source: str = "ANSADE/CN"
    warnings: list[str] = []
