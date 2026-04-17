import time
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.predictor import unified_credit_assessment
from app.db.models.application import CreditApplication
from app.db.models.prediction import PredictionLog
from app.services.audit_service import log_prediction_audit
from app.core.logging import get_logger

logger = get_logger(__name__)


async def run_prediction(
    applicant_data: dict,
    db: AsyncSession,
    applicant_ref: Optional[str] = None,
    include_shap: bool = True,
) -> dict:
    """
    Full business logic flow:
    1. Persist the incoming application to DB
    2. Run ML prediction
    3. Persist the prediction log to DB
    4. Write audit entry
    5. Return the full response

    applicant_data: raw dict from the API request (extra fields are fine — model handles them)
    """

    # ── 1. Save application record ────────────────────────────────────────────
    application = CreditApplication(
        id=uuid.uuid4(),
        applicant_ref=applicant_ref,
        annual_income_rs=float(applicant_data.get("ANNUAL_INCOME_RS") or 0),
        loan_amount_rs=float(applicant_data.get("LOAN_AMOUNT_RS") or 0),
        monthly_emi_rs=float(applicant_data.get("MONTHLY_EMI_RS") or 0),
        age_years=float(applicant_data.get("AGE_YEARS") or 0),
        employment_years=float(applicant_data.get("EMPLOYMENT_YEARS") or 0),
        cibil_score_source_2=float(applicant_data.get("CIBIL_SCORE_SOURCE_2") or 0),
        has_bureau_npa_history=int(applicant_data.get("HAS_BUREAU_NPA_HISTORY") or 0),
        total_prev_applications=int(applicant_data.get("TOTAL_PREV_APPLICATIONS") or 0),
        raw_input=applicant_data,
        status="PENDING",
    )
    db.add(application)
    await db.flush()  # get the generated ID without committing yet
    logger.info(f"Application saved: {application.id}")

    # ── 2. Run ML prediction ──────────────────────────────────────────────────
    start_ms = time.time()
    try:
        result = unified_credit_assessment(applicant_data, include_shap=include_shap)
    except Exception as e:
        application.status = "ERROR"
        await db.commit()
        logger.error(f"Prediction failed for application {application.id}: {e}")
        raise

    latency_ms = round((time.time() - start_ms) * 1000, 2)
    application.scoring_path = result["scoring_path"]
    application.status = "SCORED"

    # ── 3. Save prediction log ────────────────────────────────────────────────
    prediction_log = PredictionLog(
        id=uuid.uuid4(),
        application_id=application.id,
        scoring_path=result["scoring_path"],
        credit_score=result["credit_score"],
        default_probability=result["default_probability"],
        score_band=result["score_band"],
        decision=result["decision"],
        npa_category=result.get("npa_category"),
        rbi_classification=result.get("rbi_classification"),
        max_loan_eligible_rs=result.get("max_loan_eligible_rs", 0),
        interest_rate_pct=result.get("interest_rate_pct"),
        full_response=result,
        latency_ms=latency_ms,
        model_version="v1.0",
    )
    db.add(prediction_log)
    await db.commit()
    logger.info(
        f"Prediction complete | app={application.id} | score={result['credit_score']} "
        f"| decision={result['decision']} | latency={latency_ms}ms"
    )

    # ── 4. Audit log ──────────────────────────────────────────────────────────
    await log_prediction_audit(
        application_id=str(application.id),
        result=result,
        latency_ms=latency_ms,
    )

    # ── 5. Return response ────────────────────────────────────────────────────
    result["application_id"] = str(application.id)
    result["latency_ms"] = latency_ms
    return result