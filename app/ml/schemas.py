from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


# ── Input Schema ──────────────────────────────────────────────────────────────

class BankedApplicantInput(BaseModel):
    """Fields for applicants who have a credit/bureau history (BANKED path)."""
    # Core financials
    ANNUAL_INCOME_RS:        float  = Field(..., gt=0,  description="Annual income in ₹")
    LOAN_AMOUNT_RS:          float  = Field(..., gt=0,  description="Loan amount requested in ₹")
    MONTHLY_EMI_RS:          float  = Field(0,  ge=0,  description="Expected monthly EMI in ₹")
    AGE_YEARS:               float  = Field(..., ge=18, le=80, description="Applicant age in years")
    EMPLOYMENT_YEARS:        float  = Field(0,  ge=0,  description="Years in current employment")

    # Credit history signals
    CIBIL_SCORE_SOURCE_2:    Optional[float] = Field(None, ge=0, le=1, description="Normalised CIBIL score (0–1)")
    HAS_BUREAU_NPA_HISTORY:  Optional[int]   = Field(None, ge=0, le=1)
    TOTAL_PREV_APPLICATIONS: Optional[int]   = Field(None, ge=0)
    PREV_APPROVAL_RATE:      Optional[float] = Field(None, ge=0, le=1)

    # Personal info
    GENDER:                  Optional[str]   = None
    MARITAL_STATUS:          Optional[str]   = None
    NUMBER_OF_DEPENDENTS:    Optional[int]   = Field(None, ge=0)
    FAMILY_SIZE:             Optional[int]   = Field(None, ge=1)
    HOUSING_TYPE:            Optional[str]   = None
    EMPLOYMENT_TYPE:         Optional[str]   = None
    EDUCATION_LEVEL:         Optional[str]   = None
    OCCUPATION:              Optional[str]   = None
    EMPLOYER_SECTOR:         Optional[str]   = None

    # Location
    CITY_TIER:               Optional[int]   = Field(None, ge=1, le=3)
    REGION_POPULATION_DENSITY: Optional[float] = None

    # Asset info
    OWNS_VEHICLE:            Optional[str]   = None  # Y/N
    OWNS_PROPERTY:           Optional[str]   = None  # Y/N

    # KYC / contact
    HAS_MOBILE:              Optional[int]   = Field(None, ge=0, le=1)
    HAS_EMAIL:               Optional[int]   = Field(None, ge=0, le=1)
    AADHAAR_SUBMITTED:       Optional[int]   = Field(None, ge=0, le=1)
    PAN_SUBMITTED:           Optional[int]   = Field(None, ge=0, le=1)
    BANK_STATEMENT_SUBMITTED: Optional[int]  = Field(None, ge=0, le=1)
    INCOME_PROOF_SUBMITTED:  Optional[int]   = Field(None, ge=0, le=1)

    # Applicant reference (optional, for tracking — not used in scoring)
    applicant_ref:           Optional[str]   = Field(None, max_length=64)

    model_config = {"extra": "allow"}   # allow extra fields — passed through to model


class UnbankedApplicantInput(BaseModel):
    """Fields for applicants with income but no credit history (UNBANKED_ML path)."""
    ANNUAL_INCOME_RS:        float  = Field(..., gt=0)
    LOAN_AMOUNT_RS:          float  = Field(..., gt=0)
    MONTHLY_EMI_RS:          float  = Field(0,  ge=0)
    AGE_YEARS:               float  = Field(..., ge=18, le=80)
    EMPLOYMENT_YEARS:        float  = Field(0,  ge=0)
    EMPLOYMENT_TYPE:         Optional[str] = None
    EDUCATION_LEVEL:         Optional[str] = None
    CITY_TIER:               Optional[int] = Field(None, ge=1, le=3)
    OWNS_PROPERTY:           Optional[str] = None
    AADHAAR_SUBMITTED:       Optional[int] = Field(None, ge=0, le=1)
    PAN_SUBMITTED:           Optional[int] = Field(None, ge=0, le=1)
    applicant_ref:           Optional[str] = Field(None, max_length=64)

    model_config = {"extra": "allow"}


class AlternativeApplicantInput(BaseModel):
    """Fields for truly unbanked applicants — UPI / utility / KYC signals."""
    # UPI behaviour
    upi_transactions_per_month: int   = Field(0, ge=0)
    avg_upi_amount_rs:          float = Field(0, ge=0)

    # Utility bills
    utility_bills_paid:         int   = Field(0, ge=0)
    total_utility_bills:        int   = Field(12, ge=1)
    types_of_bills:             int   = Field(1, ge=0)

    # Mobile
    mobile_years_active:        float = Field(0, ge=0)
    same_number:                int   = Field(1, ge=0, le=1)
    prepaid_or_postpaid:        str   = "prepaid"

    # Income (informal)
    monthly_income_rs:          float = Field(0, ge=0)
    employment_type:            str   = "Daily_Wage"
    employment_years:           float = Field(0, ge=0)

    # KYC
    has_aadhaar:                int   = Field(1, ge=0, le=1)
    has_pan:                    int   = Field(0, ge=0, le=1)
    has_bank_statement:         int   = Field(0, ge=0, le=1)
    has_income_proof:           int   = Field(0, ge=0, le=1)
    has_property_doc:           int   = Field(0, ge=0, le=1)

    # Rent
    rent_paid_months:           int   = Field(0, ge=0)
    total_months_rented:        int   = Field(12, ge=1)
    owns_house:                 int   = Field(0, ge=0, le=1)

    # Demographics
    age_years:                  float = Field(30, ge=18, le=80)
    number_of_dependents:       int   = Field(0, ge=0)
    city_tier:                  int   = Field(2, ge=1, le=3)
    education_level:            str   = "Higher_Secondary_12th"

    applicant_ref:              Optional[str] = Field(None, max_length=64)

    model_config = {"extra": "allow"}


class UnifiedApplicantInput(BaseModel):
    """
    Single endpoint input — system auto-routes to the correct scoring path.
    Pass whatever fields you have; the engine determines BANKED / UNBANKED_ML / ALTERNATIVE_DATA.
    """
    applicant_ref:              Optional[str]   = Field(None, max_length=64)
    include_shap:               bool            = Field(True, description="Include SHAP explanation in response")

    model_config = {"extra": "allow"}


# ── Output Schemas ────────────────────────────────────────────────────────────

class ExplanationOut(BaseModel):
    method:           str
    risk_factors:     Dict[str, float] = {}
    strength_factors: Dict[str, float] = {}
    score_breakdown:  Optional[Dict[str, str]] = None


class PredictionOut(BaseModel):
    application_id:       Optional[str] = None
    scoring_path:         str
    credit_score:         int
    default_probability:  float          = Field(..., description="Default probability as percentage (0–100)")
    score_band:           str
    risk_description:     str
    decision:             str            = Field(..., description="APPROVE | CONDITIONAL | REJECT")
    npa_category:         str
    rbi_classification:   str
    max_loan_eligible_rs: float
    interest_rate_pct:    Optional[float] = None
    reasoning:            List[str]       = []
    explanation:          Optional[ExplanationOut] = None
    latency_ms:           Optional[float] = None


class HealthOut(BaseModel):
    status:       str
    models_loaded: Dict[str, bool]
    version:      str
    environment:  str


class AdminStatsOut(BaseModel):
    total_predictions:    int
    approve_count:        int
    reject_count:         int
    conditional_count:    int
    avg_credit_score:     float
    avg_default_probability: float
    path_breakdown:       Dict[str, int]