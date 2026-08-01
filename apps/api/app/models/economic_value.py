from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EconomicValue(Base):
    __tablename__ = "economic_values"
    __table_args__ = (
        UniqueConstraint("dataset_id", "indicator_id", "year", name="uq_economic_value_identity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    original_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_missing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quality_flag: Mapped[str] = mapped_column(String(30), nullable=False, default="ok")
    source_row: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_column: Mapped[str | None] = mapped_column(String(20), nullable=True)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="values")
    indicator: Mapped["Indicator"] = relationship("Indicator", back_populates="values")
