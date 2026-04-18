from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Indian Credit Scoring API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/credit_scoring_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Models
    MODEL_DIR: str = "models"
    MODEL_BANKED_FILE: str = "model_banked.pkl"
    MODEL_UNBANKED_FILE: str = "model_unbanked.pkl"
    SHAP_EXPLAINER_BANKED_FILE: str = "shap_explainer_banked.pkl"
    SHAP_EXPLAINER_UNBANKED_FILE: str = "shap_explainer_unbanked.pkl"
    ALTERNATIVE_SCORING_ENGINE_FILE: str = "alternative_scoring_engine.pkl"

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()