from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.api.v1.router import api_v1_router
from app.ml.model_loader import load_all_models
from app.db.session import engine
from app.db.base import Base
import app.db.models  # noqa: F401 — registers models with SQLAlchemy metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──────────────────────────────────────────────
    setup_logging()
    load_all_models()
    # Create DB tables if they don't exist (use Alembic for prod migrations)
   # async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.create_all)
    yield
    # ── SHUTDOWN ─────────────────────────────────────────────
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Indian Credit Scoring System — Banked, Unbanked & Alternative Data paths",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
register_exception_handlers(app)

# Routes
app.include_router(api_v1_router, prefix="/api/v1")