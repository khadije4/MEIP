from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetRead

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("", response_model=list[DatasetRead])
def list_datasets(db: Session = Depends(get_db)) -> list[Dataset]:
    return db.query(Dataset).order_by(Dataset.table_number).all()


@router.get("/{code}", response_model=DatasetRead)
def get_dataset(code: str, db: Session = Depends(get_db)) -> Dataset:
    dataset = db.query(Dataset).filter(Dataset.code == code).first()
    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "dataset_not_found",
                "message_en": "Dataset not found.",
                "message_ar": "مجموعة البيانات غير موجودة.",
                "message_fr": "Jeu de données introuvable.",
            },
        )
    return dataset
