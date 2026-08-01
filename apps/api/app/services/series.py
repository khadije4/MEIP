"""DB query helpers that feed the pure analytics functions. Analytics never
take a DB session directly; routers/services fetch series here and pass
plain dicts into app/analytics/*."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.economic_value import EconomicValue
from app.models.indicator import Indicator


def get_indicator_or_404(db: Session, code: str) -> Indicator:
    indicator = db.query(Indicator).filter(Indicator.code == code).first()
    if indicator is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "indicator_not_found",
                "message_en": f"Indicator '{code}' not found.",
                "message_ar": "المؤشر غير موجود.",
                "message_fr": "Indicateur introuvable.",
            },
        )
    return indicator


def get_ok_series(db: Session, code: str) -> dict[int, float]:
    """year -> value, restricted to cleanly-parsed ('ok') observations only.
    Missing/nonnumeric years are simply absent, never zero-filled."""
    indicator = get_indicator_or_404(db, code)
    rows = (
        db.query(EconomicValue)
        .filter(EconomicValue.indicator_id == indicator.id, EconomicValue.quality_flag == "ok")
        .all()
    )
    return {row.year: row.value for row in rows}


def get_ok_series_by_code(db: Session, codes: list[str]) -> dict[str, dict[int, float]]:
    return {code: get_ok_series(db, code) for code in codes}


def get_full_points(db: Session, code: str) -> list[EconomicValue]:
    indicator = get_indicator_or_404(db, code)
    return (
        db.query(EconomicValue)
        .filter(EconomicValue.indicator_id == indicator.id)
        .order_by(EconomicValue.year)
        .all()
    )
