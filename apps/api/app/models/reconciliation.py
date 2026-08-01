from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReconciliationIssue(Base):
    __tablename__ = "reconciliation_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    first_indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id"), nullable=False)
    second_indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id"), nullable=False)
    first_value: Mapped[float] = mapped_column(Float, nullable=False)
    second_value: Mapped[float] = mapped_column(Float, nullable=False)
    absolute_difference: Mapped[float] = mapped_column(Float, nullable=False)
    percentage_difference: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    explanation_fr: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_ar: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    first_indicator: Mapped["Indicator"] = relationship("Indicator", foreign_keys=[first_indicator_id])
    second_indicator: Mapped["Indicator"] = relationship("Indicator", foreign_keys=[second_indicator_id])
