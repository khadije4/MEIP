from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, model_validator


class ReportRequest(BaseModel):
    indicator_code: str
    start_year: int | None = None
    end_year: int | None = None
    language: Literal["fr", "ar"] = "fr"
    format: Literal["pdf", "csv"] = "pdf"
    include_forecast: bool = True

    @model_validator(mode="after")
    def validate_period(self):
        if self.start_year is not None and self.end_year is not None and self.start_year > self.end_year:
            raise ValueError("start_year must be less than or equal to end_year")
        return self
