from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class IndicatorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    original_label: str
    name_fr: str
    name_ar: str | None
    category: str
    parent_indicator_id: int | None
    hierarchy_level: int
    unit: str
    source_side: str
    is_aggregate: bool
    is_alias: bool
    alias_of_indicator_id: int | None


class IndicatorSeriesPoint(BaseModel):
    year: int
    value: float | None
    is_missing: bool
    quality_flag: str


class IndicatorSeries(BaseModel):
    indicator: IndicatorRead
    dataset_code: str
    unit: str
    points: list[IndicatorSeriesPoint]
