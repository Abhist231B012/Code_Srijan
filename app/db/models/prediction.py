import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # FK back to the application
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("credit_applications.id", ondelete="CASCADE"),
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # ML output
    scoring_path: Mapped[str] = mapped_column(String(32))
    credit_score: Mapped[int] = mapped_column(Integer)
    default_probability: Mapped[float] = mapped_column(Float)   # 0–100
    score_band: Mapped[str] = mapped_column(String(16))          # EXCELLENT / GOOD / FAIR / POOR / VERY POOR
    decision: Mapped[str] = mapped_column(String(16))            # APPROVE / CONDITIONAL / REJECT

    # RBI / NPA classification
    npa_category: Mapped[str] = mapped_column(String(64), nullable=True)
    rbi_classification: Mapped[str] = mapped_column(String(16), nullable=True)

    # Loan recommendation
    max_loan_eligible_rs: Mapped[float] = mapped_column(Float, nullable=True)
    interest_rate_pct: Mapped[float] = mapped_column(Float, nullable=True)

    # Full prediction payload + reasoning
    full_response: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Model version tag (useful for drift monitoring)
    model_version: Mapped[str] = mapped_column(String(32), nullable=True, default="v1.0")

    # Latency tracking (milliseconds)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<PredictionLog id={self.id} score={self.credit_score} "
            f"decision={self.decision} path={self.scoring_path}>"
        )