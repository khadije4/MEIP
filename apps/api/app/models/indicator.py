from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    original_label: Mapped[str] = mapped_column(String(500), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="unmapped")
    parent_indicator_id: Mapped[int | None] = mapped_column(
        ForeignKey("indicators.id"), nullable=True
    )
    hierarchy_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit: Mapped[str] = mapped_column(String(120), nullable=False, default="Unit not confirmed")
    source_side: Mapped[str] = mapped_column(String(20), nullable=False)  # expenditure | activity
    is_aggregate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_alias: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alias_of_indicator_id: Mapped[int | None] = mapped_column(
        ForeignKey("indicators.id"), nullable=True
    )

    parent: Mapped["Indicator | None"] = relationship(
        "Indicator", remote_side=[id], foreign_keys=[parent_indicator_id], back_populates="children"
    )
    children: Mapped[list["Indicator"]] = relationship(
        "Indicator", foreign_keys=[parent_indicator_id], back_populates="parent"
    )
    alias_of: Mapped["Indicator | None"] = relationship(
        "Indicator", remote_side=[id], foreign_keys=[alias_of_indicator_id]
    )
    values: Mapped[list["EconomicValue"]] = relationship("EconomicValue", back_populates="indicator")
