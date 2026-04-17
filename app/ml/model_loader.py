import os
import joblib
from app.config import settings
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
# ── Global model registry (loaded once at startup) ────────────────────────────
_models: dict = {}
 
 
def load_all_models():
    """
    Called once during FastAPI lifespan startup.
    Loads all .pkl files into memory, plus the rule-based alternative engine.
    """
    model_dir = settings.MODEL_DIR
 
    # ── PKL-based models ──────────────────────────────────────────────────────
    files = {
        "model_banked":          settings.MODEL_BANKED_FILE,
        "model_unbanked":        settings.MODEL_UNBANKED_FILE,
        "shap_banked":           settings.SHAP_EXPLAINER_BANKED_FILE,
        "shap_unbanked":         settings.SHAP_EXPLAINER_UNBANKED_FILE,
        "feature_cols_banked":   "feature_columns.pkl",
        "feature_cols_unbanked": "feature_columns_unbanked.pkl",
    }
 
    for key, filename in files.items():
        path = os.path.join(model_dir, filename)
        if os.path.exists(path):
            try:
                _models[key] = joblib.load(path)
                logger.info(f"✅ Loaded model [{key}] from {path}")
            except Exception as e:
                logger.error(f"❌ Failed to load [{key}] from {path}: {e}")
        else:
            logger.warning(
                f"⚠️  Model file not found: {path} — [{key}] will be unavailable"
            )
 
    # ── Alternative scoring engine (rule-based — no pkl needed) ──────────────
    try:
        from app.ml.alternative_engine import AltScoringEngine
        _models["alt_scoring_engine"] = AltScoringEngine()
        logger.info("✅ Loaded model [alt_scoring_engine] from AlternativeScoringEngine class")
    except Exception as e:
        logger.error(f"❌ Failed to load [alt_scoring_engine]: {e}")
 
 
def get_model(key: str):
    """Returns the model for the given key. Raises if not loaded."""
    model = _models.get(key)
    if model is None:
        from app.core.exceptions import ModelNotLoadedError
        raise ModelNotLoadedError(
            f"Model '{key}' is not loaded. Check models/ directory."
        )
    return model
 
 
def get_model_optional(key: str):
    """Returns None instead of raising if model is not loaded."""
    return _models.get(key)
 
 
def models_status() -> dict:
    """Returns a dict of which models are loaded (used by /health endpoint)."""
    return {k: (v is not None) for k, v in _models.items()}