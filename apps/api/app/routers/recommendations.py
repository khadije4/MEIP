from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recommendations import CatalogueEntry, RecommendationGenerateRequest, RecommendationResponse
from app.services import recommendations as service
from app.services.series import get_indicator_or_404

router=APIRouter(prefix="/api/recommendations",tags=["recommendations"])

@router.post("/generate",response_model=RecommendationResponse)
def generate(payload: RecommendationGenerateRequest,db:Session=Depends(get_db)):
    return service.generate(db,payload.year,[s.model_dump() for s in payload.shocks],payload.shock_duration,
      objective=payload.objective,budget_level=payload.budget_level,implementation_horizon=payload.implementation_horizon)

@router.get("/catalogue",response_model=list[CatalogueEntry])
def catalogue():
    return [{"sector_code":code,"recommendations":service.catalogue_for(code),"monitoring_indicators":service.MONITORING.get(code,[code,"gdp_activity_market_prices"])} for code in service.SECTOR_ACTIONS]

@router.get("/sectors/{indicator_code}",response_model=CatalogueEntry)
def sector(indicator_code:str,db:Session=Depends(get_db)):
    indicator=get_indicator_or_404(db,indicator_code); canonical=indicator.alias_of.code if indicator.is_alias and indicator.alias_of else indicator.code
    return {"sector_code":canonical,"recommendations":service.catalogue_for(canonical),"monitoring_indicators":service.MONITORING.get(canonical,[canonical,"gdp_activity_market_prices"])}

@router.get("/monitoring-indicators/{indicator_code}")
def monitoring(indicator_code:str,db:Session=Depends(get_db)):
    indicator=get_indicator_or_404(db,indicator_code); canonical=indicator.alias_of.code if indicator.is_alias and indicator.alias_of else indicator.code
    return {"sector_code":canonical,"indicator_codes":service.MONITORING.get(canonical,[canonical,"gdp_activity_market_prices"]),"source":"ANSADE/CN"}

