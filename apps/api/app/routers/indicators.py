from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.growth import summarize
from app.database import get_db
from app.models.indicator import Indicator
from app.schemas.analytics import SummaryOut
from app.schemas.indicator import IndicatorRead, IndicatorSeries, IndicatorSeriesPoint
from app.services.series import get_full_points, get_indicator_or_404, get_ok_series

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("", response_model=list[IndicatorRead])
def list_indicators(
    source_side: str | None = None, category: str | None = None, db: Session = Depends(get_db)
) -> list[Indicator]:
    query = db.query(Indicator)
    if source_side:
        query = query.filter(Indicator.source_side == source_side)
    if category:
        query = query.filter(Indicator.category == category)
    return query.order_by(Indicator.source_side, Indicator.hierarchy_level, Indicator.code).all()


@router.get("/{code}", response_model=IndicatorRead)
def get_indicator(code: str, db: Session = Depends(get_db)) -> Indicator:
    return get_indicator_or_404(db, code)


@router.get("/{code}/series", response_model=IndicatorSeries)
def get_indicator_series(code: str, db: Session = Depends(get_db)) -> IndicatorSeries:
    indicator = get_indicator_or_404(db, code)
    points = get_full_points(db, code)
    dataset_code = points[0].dataset.code if points else ""
    return IndicatorSeries(
        indicator=indicator,
        dataset_code=dataset_code,
        unit=indicator.unit,
        points=[
            IndicatorSeriesPoint(
                year=p.year, value=p.value, is_missing=p.is_missing, quality_flag=p.quality_flag
            )
            for p in points
        ],
    )


@router.get("/{code}/summary", response_model=SummaryOut)
def get_indicator_summary(code: str, db: Session = Depends(get_db)) -> SummaryOut:
    get_indicator_or_404(db, code)
    series = get_ok_series(db, code)
    summary = summarize(series)
    return SummaryOut(**summary.__dict__)
