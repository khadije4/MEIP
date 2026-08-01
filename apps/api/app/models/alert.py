from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EconomicAlert(Base):
    __tablename__ = "economic_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(60), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    observed_value: Mapped[float] = mapped_column(Float, nullable=False)
    expected_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentage_change: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation_fr: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_ar: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    indicator: Mapped["Indicator"] = relationship("Indicator")
