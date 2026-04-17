from fastapi import APIRouter
from app.ml.model_loader import models_status
from app.ml.schemas import HealthOut
from app.config import settings

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthOut,
    summary="Health Check",
    description="Returns API health status and which ML models are currently loaded.",
)
async def health():
    loaded = models_status()
    all_critical_loaded = loaded.get("model_banked") and loaded.get("model_unbanked")

    return {
        "status": "ok" if all_critical_loaded else "degraded",
        "models_loaded": loaded,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ping", summary="Simple ping")
async def ping():
    return {"pong": True}