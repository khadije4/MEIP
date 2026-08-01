from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.ingestion.seed import seed_indicators
from app.routers import activity, analytics, assistant, dashboard, data, datasets, expenditure, forecast, health, indicators, recommendations, reports, stress_test

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("meip")

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(datasets.router)
app.include_router(data.router)
app.include_router(indicators.router)
app.include_router(dashboard.router)
app.include_router(activity.router)
app.include_router(expenditure.router)
app.include_router(analytics.router)
app.include_router(forecast.router)
app.include_router(assistant.router)
app.include_router(reports.router)
app.include_router(stress_test.router)
app.include_router(recommendations.router)


@app.get("/", tags=["meta"])
def api_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "running",
        "health": "/api/health",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "frontend": "Use this server's Wi-Fi address on port 5173.",
    }


@app.exception_handler(HTTPException)
async def structured_http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        return JSONResponse(status_code=exc.status_code, content={"error": detail})
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message_en": "An unexpected error occurred.",
                "message_ar": "حدث خطأ غير متوقع.",
                "message_fr": "Une erreur inattendue s'est produite.",
            }
        },
    )


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        created = seed_indicators(db)
        logger.info("Indicator taxonomy seeded (%d new rows).", created)
    finally:
        db.close()
