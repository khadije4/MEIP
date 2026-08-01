from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analytics.forecasting import InsufficientObservationsError, generate_forecast
from app.database import get_db
from app.schemas.analytics import ForecastRequest, ForecastResponseOut, SeriesPoint
from app.services.series import get_indicator_or_404, get_ok_series

router = APIRouter(prefix="/api", tags=["forecast"])

# Only inventory changes are structurally allowed to be negative in this
# dataset (Variations de stock); every other indicator is clamped at 0.
_ALLOW_NEGATIVE_CODES = {"inventory_changes"}

_DISCLAIMER_FR = (
    "Cette prévision est une estimation expérimentale calculée à partir de méthodes "
    "statistiques classiques. Elle ne constitue pas une statistique officielle de l'ANSADE."
)
_DISCLAIMER_AR = (
    "هذا التوقع تقدير تجريبي محسوب باستخدام أساليب إحصائية كلاسيكية. وهو لا يمثل "
    "إحصاءً رسميًا صادرًا عن الوكالة الوطنية للإحصاء."
)


@router.post("/forecast", response_model=ForecastResponseOut)
def forecast(body: ForecastRequest, db: Session = Depends(get_db)) -> ForecastResponseOut:
    ind = get_indicator_or_404(db, body.indicator_code)
    full_series = get_ok_series(db, body.indicator_code)
    series = {y: v for y, v in full_series.items() if (body.start_year is None or y >= body.start_year) and (body.end_year is None or y <= body.end_year)}
    horizon = body.requested_horizon

    try:
        result = generate_forecast(
            series, horizon=horizon, non_negative=body.indicator_code not in _ALLOW_NEGATIVE_CODES,
            preferred_model=body.preferred_model,
        )
    except InsufficientObservationsError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "insufficient_observations",
                "message_en": str(exc),
                "message_ar": f"عدد المشاهدات ({exc.count}) غير كافٍ لإجراء توقع موثوق (الحد الأدنى 8).",
                "message_fr": f"Nombre d'observations ({exc.count}) insuffisant pour une prévision fiable (minimum 8).",
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "invalid_forecast_parameter", "message_en": str(exc), "message_fr": "Parametre de prevision invalide.", "message_ar": "معامل التوقع غير صالح."}) from exc

    years = sorted(series)
    missing_years = [y for y in range(years[0], years[-1] + 1) if y not in series] if years else []
    warnings = []
    if missing_years:
        warnings.append("Missing calendar years were excluded and chronological order was preserved: " + ", ".join(map(str, missing_years)))
    if result.limited_data_warning:
        warnings.append("Limited historical data reduces forecast reliability.")

    return ForecastResponseOut(
        indicator_code=ind.code,
        name_fr=ind.name_fr,
        name_ar=ind.name_ar,
        unit=ind.unit,
        historical=[SeriesPoint(year=y, value=v) for y, v in sorted(series.items())],
        model_name=result.model_name,
        baseline_model=result.baseline_model,
        horizon_years=result.horizon_years,
        predicted_values=result.predicted_values,
        lower_bounds=result.lower_bounds,
        upper_bounds=result.upper_bounds,
        mae=result.mae,
        mape=result.mape,
        baseline_mae=result.baseline_mae,
        baseline_mape=result.baseline_mape,
        reliability=result.reliability,
        limited_data_warning=result.limited_data_warning,
        observation_count=result.observation_count,
        clamped_to_zero=result.clamped_to_zero,
        disclaimer_fr=_DISCLAIMER_FR,
        disclaimer_ar=_DISCLAIMER_AR,
        historical_start_year=years[0] if years else None,
        historical_end_year=years[-1] if years else None,
        warnings=warnings,
    )
