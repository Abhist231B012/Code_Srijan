import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class CreditApplication(Base):
    __tablename__ = "credit_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Applicant identity (anonymised — no PII stored)
    applicant_ref: Mapped[str] = mapped_column(String(64), nullable=True, index=True)

    # Core financial inputs
    annual_income_rs: Mapped[float] = mapped_column(Float, nullable=True)
    loan_amount_rs: Mapped[float] = mapped_column(Float, nullable=True)
    monthly_emi_rs: Mapped[float] = mapped_column(Float, nullable=True)
    age_years: Mapped[float] = mapped_column(Float, nullable=True)
    employment_years: Mapped[float] = mapped_column(Float, nullable=True)

    # Credit history flags
    cibil_score_source_2: Mapped[float] = mapped_column(Float, nullable=True)
    has_bureau_npa_history: Mapped[int] = mapped_column(Integer, nullable=True)
    total_prev_applications: Mapped[int] = mapped_column(Integer, nullable=True)

    # Scoring path determined by the system
    scoring_path: Mapped[str] = mapped_column(
        SAEnum("BANKED", "UNBANKED_ML", "ALTERNATIVE_DATA", name="scoring_path_enum"),
        nullable=True,
    )

    # Full raw input payload stored as JSON for audit / replay
    raw_input: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        SAEnum("PENDING", "SCORED", "ERROR", name="application_status_enum"),
        default="PENDING",
    )

    def __repr__(self) -> str:
        return f"<CreditApplication id={self.id} path={self.scoring_path}>"