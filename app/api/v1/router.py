from fastapi import APIRouter
from app.api.v1.routes import predict, health, admin

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(predict.router, tags=["Prediction"])
api_v1_router.include_router(admin.router, tags=["Admin"])