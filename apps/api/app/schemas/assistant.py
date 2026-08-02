from __future__ import annotations

from pydantic import BaseModel, Field
from app.schemas.recommendations import RecommendationResponse


class AssistantQuery(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    language: str | None = None
    last_indicator_codes: list[str] = Field(default_factory=list)
    last_year: int | None = None


class EvidenceValue(BaseModel):
    indicator_code: str
    indicator_name: str
    year: int
    value: float
    source_side: str
    source_file: str
    worksheet: str
    unit: str


class AssistantAnswer(BaseModel):
    language: str
    intent: str
    answer: str
    values_used: list[EvidenceValue]
    calculation: str
    source: str = "ANSADE/CN"
    warnings: list[str] = []
    supported: bool = True
    recommendation_plan: RecommendationResponse | None = None
