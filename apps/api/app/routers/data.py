from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.ingestion.service import import_all
from app.models.dataset import Dataset
from app.models.economic_value import EconomicValue
from app.models.indicator import Indicator
from app.models.reconciliation import ReconciliationIssue
from app.schemas.dataset import DataStatus, DatasetQuality, ReconciliationEntry

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/import")
def import_data(db: Session = Depends(get_db)) -> dict:
    settings = get_settings()
    try:
        report = import_all(db, Path(settings.data_raw_dir), Path(settings.data_processed_dir))
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "source_file_missing",
                "message_en": str(exc),
                "message_ar": "أحد ملفات المصدر غير موجود في data/raw.",
                "message_fr": "Un des fichiers source est introuvable dans data/raw.",
            },
        ) from exc
    return report


@router.get("/status", response_model=DataStatus)
def data_status(db: Session = Depends(get_db)) -> DataStatus:
    datasets = db.query(Dataset).order_by(Dataset.table_number).all()
    indicator_count = db.query(func.count(Indicator.id)).scalar() or 0
    total_observations = db.query(func.count(EconomicValue.id)).scalar() or 0
    last_import_at = db.query(func.max(Dataset.imported_at)).scalar()

    return DataStatus(
        imported=len(datasets) > 0,
        datasets=datasets,
        indicator_count=indicator_count,
        total_observations=total_observations,
        last_import_at=last_import_at,
    )


@router.get("/quality", response_model=list[DatasetQuality])
def data_quality(db: Session = Depends(get_db)) -> list[DatasetQuality]:
    results: list[DatasetQuality] = []
    for dataset in db.query(Dataset).order_by(Dataset.table_number).all():
        values = db.query(EconomicValue).filter(EconomicValue.dataset_id == dataset.id).all()
        total = len(values)
        ok_count = sum(1 for v in values if v.quality_flag == "ok")
        missing_count = sum(1 for v in values if v.quality_flag == "missing")
        nonnumeric_count = sum(1 for v in values if v.quality_flag == "nonnumeric")
        completeness = (ok_count / total * 100) if total else 0.0
        results.append(
            DatasetQuality(
                dataset_code=dataset.code,
                total_values=total,
                ok_count=ok_count,
                missing_count=missing_count,
                nonnumeric_count=nonnumeric_count,
                completeness_score=round(completeness, 2),
            )
        )
    return results


@router.get("/reconciliation", response_model=list[ReconciliationEntry])
def data_reconciliation(db: Session = Depends(get_db)) -> list[ReconciliationEntry]:
    first_ind = Indicator.__table__.alias("first_ind")
    second_ind = Indicator.__table__.alias("second_ind")

    rows = (
        db.query(ReconciliationIssue, first_ind.c.code, second_ind.c.code)
        .join(first_ind, ReconciliationIssue.first_indicator_id == first_ind.c.id)
        .join(second_ind, ReconciliationIssue.second_indicator_id == second_ind.c.id)
        .order_by(ReconciliationIssue.year)
        .all()
    )

    return [
        ReconciliationEntry(
            id=issue.id,
            year=issue.year,
            first_indicator_code=first_code,
            second_indicator_code=second_code,
            first_value=issue.first_value,
            second_value=issue.second_value,
            absolute_difference=issue.absolute_difference,
            percentage_difference=issue.percentage_difference,
            severity=issue.severity,
            explanation_fr=issue.explanation_fr,
            explanation_ar=issue.explanation_ar,
        )
        for issue, first_code, second_code in rows
    ]
