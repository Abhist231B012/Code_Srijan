import json
import os
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger(__name__)

AUDIT_LOG_PATH = os.environ.get("AUDIT_LOG_PATH", "logs/audit.jsonl")


async def log_prediction_audit(
    application_id: str,
    result: dict,
    latency_ms: float,
):
    """
    Writes a structured JSONL audit entry for every prediction.
    Useful for RBI compliance, model drift monitoring, and review.
    Each line is a valid JSON object — easy to ingest into ELK / BigQuery.
    """
    entry = {
        "timestamp":          datetime.utcnow().isoformat() + "Z",
        "application_id":     application_id,
        "scoring_path":       result.get("scoring_path"),
        "credit_score":       result.get("credit_score"),
        "default_probability":result.get("default_probability"),
        "score_band":         result.get("score_band"),
        "decision":           result.get("decision"),
        "npa_category":       result.get("npa_category"),
        "rbi_classification": result.get("rbi_classification"),
        "max_loan_eligible_rs": result.get("max_loan_eligible_rs"),
        "interest_rate_pct":  result.get("interest_rate_pct"),
        "latency_ms":         latency_ms,
        "model_version":      "v1.0",
    }

    try:
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        # Audit logging should never crash the prediction response
        logger.warning(f"Audit log write failed: {e}")