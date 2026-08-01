from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.stress_test import (ConcentrationResponse, DependencyResponse, MultipleShockRequest,
    MultipleShockResponse, PresetScenario, RankingResponse, SingleShockRequest, SingleShockResponse)
from app.services import stress_test as service

router = APIRouter(prefix="/api/stress-test", tags=["stress-test"])

@router.post("/single", response_model=SingleShockResponse)
def single(payload: SingleShockRequest, db: Session = Depends(get_db)):
    return service.single(db, payload.year, payload.indicator_code, payload.shock_rate)

@router.post("/multiple", response_model=MultipleShockResponse)
def multiple(payload: MultipleShockRequest, db: Session = Depends(get_db)):
    return service.multiple(db, payload.year, [shock.model_dump() for shock in payload.shocks])

@router.get("/ranking", response_model=RankingResponse)
def ranking(year: int = Query(ge=1998, le=2024), ranking_group: str = "main_sectors", db: Session = Depends(get_db)):
    return service.ranking(db, year, ranking_group)

@router.get("/history/{indicator_code}", response_model=DependencyResponse)
def history(indicator_code: str, start_year: int | None = Query(None, ge=1998, le=2024), end_year: int | None = Query(None, ge=1998, le=2024), db: Session = Depends(get_db)):
    return service.history(db, indicator_code, start_year, end_year)

@router.get("/concentration", response_model=ConcentrationResponse)
def concentration(year: int = Query(ge=1998, le=2024), ranking_group: str = "main_sectors", db: Session = Depends(get_db)):
    return service.concentration(db, year, ranking_group)

@router.get("/presets", response_model=list[PresetScenario])
def presets():
    return [
        {"code":"extractive_shutdown","title_fr":"Arrêt complet des activités extractives","title_ar":"توقف كامل للأنشطة الاستخراجية","shocks":[{"indicator_code":"extractive_activities","shock_rate":1.0}]},
        {"code":"fishing_50","title_fr":"Baisse de 50 % de la pêche","title_ar":"انخفاض الصيد بنسبة 50٪","shocks":[{"indicator_code":"fishing","shock_rate":0.5}]},
        {"code":"construction_30","title_fr":"Baisse de 30 % du BTP","title_ar":"انخفاض البناء والأشغال العامة بنسبة 30٪","shocks":[{"indicator_code":"construction_public_works","shock_rate":0.3}]},
        {"code":"commerce_25","title_fr":"Baisse de 25 % du commerce","title_ar":"انخفاض التجارة بنسبة 25٪","shocks":[{"indicator_code":"commerce","shock_rate":0.25}]},
        {"code":"combined","title_fr":"Choc combiné extractif, pêche, commerce et transport","title_ar":"صدمة مشتركة للاستخراج والصيد والتجارة والنقل","shocks":[{"indicator_code":"extractive_activities","shock_rate":0.25},{"indicator_code":"fishing","shock_rate":0.25},{"indicator_code":"commerce","shock_rate":0.25},{"indicator_code":"transport","shock_rate":0.25}]},
    ]

