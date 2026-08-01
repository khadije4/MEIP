from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.report import ReportRequest
from app.services.series import get_indicator_or_404, get_ok_series
from app.reports.generator import generate_csv, generate_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/generate")
def generate(body: ReportRequest, db: Session = Depends(get_db)):
    indicator = get_indicator_or_404(db, body.indicator_code)
    series = {y:v for y,v in get_ok_series(db, body.indicator_code).items() if (body.start_year is None or y >= body.start_year) and (body.end_year is None or y <= body.end_year)}
    if not series:
        raise HTTPException(status_code=400, detail={"code":"report_period_empty","message_en":"No valid observations in the selected period.","message_fr":"Aucune observation valide pour la période.","message_ar":"لا توجد مشاهدات صالحة في الفترة المحددة."})
    name = (indicator.name_ar if body.language == "ar" else indicator.name_fr) or indicator.name_fr
    payload = generate_csv(name, series, indicator.unit, "ANSADE/CN") if body.format == "csv" else generate_pdf(name, series, indicator.unit, "ANSADE/CN", body.language, indicator.source_side, body.include_forecast)
    media = "text/csv; charset=utf-8" if body.format == "csv" else "application/pdf"
    filename = f"meip_{body.indicator_code}_{min(series)}_{max(series)}.{body.format}"
    # The complete report is generated in memory and returned directly. No
    # permanent or ephemeral server-side report file is required.
    return Response(content=payload, media_type=media, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
