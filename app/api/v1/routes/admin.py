from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models.prediction import PredictionLog
from app.ml.schemas import AdminStatsOut
from app.core.security import require_admin

router = APIRouter()


@router.get(
    "/admin/stats",
    response_model=AdminStatsOut,
    summary="Prediction Statistics (Admin Only)",
)
async def prediction_stats(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    # Total predictions
    total_result = await db.execute(select(func.count()).select_from(PredictionLog))
    total = total_result.scalar() or 0

    # Decision breakdown
    decision_result = await db.execute(
        select(PredictionLog.decision, func.count()).group_by(PredictionLog.decision)
    )
    decision_counts = {row[0]: row[1] for row in decision_result.fetchall()}

    # Path breakdown
    path_result = await db.execute(
        select(PredictionLog.scoring_path, func.count()).group_by(PredictionLog.scoring_path)
    )
    path_counts = {row[0]: row[1] for row in path_result.fetchall()}

    # Averages
    avg_result = await db.execute(
        select(
            func.avg(PredictionLog.credit_score),
            func.avg(PredictionLog.default_probability),
        )
    )
    avgs = avg_result.fetchone()

    return {
        "total_predictions":        total,
        "approve_count":            decision_counts.get("APPROVE", 0),
        "reject_count":             decision_counts.get("REJECT", 0),
        "conditional_count":        decision_counts.get("CONDITIONAL", 0),
        "avg_credit_score":         round(float(avgs[0] or 0), 2),
        "avg_default_probability":  round(float(avgs[1] or 0), 2),
        "path_breakdown":           path_counts,
    }


@router.get("/admin/recent", summary="Last 20 predictions (Admin Only)")
async def recent_predictions(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    result = await db.execute(
        select(PredictionLog)
        .order_by(PredictionLog.created_at.desc())
        .limit(20)
    )
    logs = result.scalars().all()
    return [
        {
            "id":                  str(log.id),
            "application_id":      str(log.application_id),
            "created_at":          log.created_at.isoformat(),
            "scoring_path":        log.scoring_path,
            "credit_score":        log.credit_score,
            "default_probability": log.default_probability,
            "score_band":          log.score_band,
            "decision":            log.decision,
            "latency_ms":          log.latency_ms,
        }
        for log in logs
    ]