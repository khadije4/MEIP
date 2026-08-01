from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    name_fr: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    worksheet_name: Mapped[str] = mapped_column(String(255), nullable=False)
    table_number: Mapped[str] = mapped_column(String(20), nullable=False)
    source_name: Mapped[str] = mapped_column(String(120), nullable=False, default="ANSADE/CN")
    unit: Mapped[str] = mapped_column(String(120), nullable=False, default="Unit not confirmed")
    price_type: Mapped[str] = mapped_column(String(30), nullable=False, default="current")
    frequency: Mapped[str] = mapped_column(String(20), nullable=False, default="annual")
    geographic_level: Mapped[str] = mapped_column(String(60), nullable=False, default="national")
    start_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    imported_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    validation_status: Mapped[str] = mapped_column(String(30), default="pending")

    values: Mapped[list["EconomicValue"]] = relationship(
        "EconomicValue", back_populates="dataset", cascade="all, delete-orphan"
    )
