from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.schemas import UnifiedApplicantInput, PredictionOut
from app.services.prediction_service import run_prediction
from app.db.session import get_db
from app.core.security import get_current_user
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionOut,
    summary="Credit Assessment",
    description=(
        "Submit an applicant's data for credit scoring. "
        "The system auto-routes to BANKED, UNBANKED_ML, or ALTERNATIVE_DATA path. "
        "Pass whatever fields you have — the engine handles missing ones gracefully."
    ),
)
async def predict(
    payload: UnifiedApplicantInput,
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    applicant_data = payload.model_dump(exclude={"applicant_ref", "include_shap"}, exclude_none=True)

    result = await run_prediction(
        applicant_data=applicant_data,
        db=db,
        applicant_ref=payload.applicant_ref,
        include_shap=payload.include_shap,
    )
    return result


@router.post(
    "/predict/batch",
    summary="Batch Credit Assessment (up to 50 applicants)",
)
async def predict_batch(
    payloads: list[UnifiedApplicantInput],
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    if len(payloads) > 50:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 50 applicants.")

    results = []
    for payload in payloads:
        applicant_data = payload.model_dump(
            exclude={"applicant_ref", "include_shap"}, exclude_none=True
        )
        result = await run_prediction(
            applicant_data=applicant_data,
            db=db,
            applicant_ref=payload.applicant_ref,
            include_shap=False,  # disable SHAP for batch for performance
        )
        results.append(result)

    return {"count": len(results), "results": results}