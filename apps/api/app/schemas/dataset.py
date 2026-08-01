from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name_fr: str
    name_ar: str | None
    original_filename: str
    worksheet_name: str
    table_number: str
    source_name: str
    unit: str
    price_type: str
    frequency: str
    geographic_level: str
    start_year: int | None
    end_year: int | None
    imported_at: dt.datetime
    validation_status: str


class DatasetQuality(BaseModel):
    dataset_code: str
    total_values: int
    ok_count: int
    missing_count: int
    nonnumeric_count: int
    completeness_score: float


class DataStatus(BaseModel):
    imported: bool
    datasets: list[DatasetRead]
    indicator_count: int
    total_observations: int
    last_import_at: dt.datetime | None


class ReconciliationEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int
    first_indicator_code: str
    second_indicator_code: str
    first_value: float
    second_value: float
    absolute_difference: float
    percentage_difference: float
    severity: str
    explanation_fr: str
    explanation_ar: str
