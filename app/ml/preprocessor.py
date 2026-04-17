import pandas as pd
import numpy as np
from app.core.logging import get_logger

logger = get_logger(__name__)


def build_feature_dataframe(applicant_data: dict, feature_columns: list) -> pd.DataFrame:
    """
    Converts raw applicant dict into the exact DataFrame the LightGBM model expects.
    - Adds engineered features (ratios, flags)
    - Fills missing columns with 0
    - Encodes any leftover string columns as 0 (LightGBM handles its own categoricals)
    - Returns df with columns in correct order
    """
    input_df = pd.DataFrame([applicant_data])

    # ── Derived ratio features ─────────────────────────────────────────────────
    annual_income = input_df.get("ANNUAL_INCOME_RS", pd.Series([1])).fillna(1)
    annual_income = annual_income.replace(0, 1)

    if "MONTHLY_EMI_RS" in input_df.columns and "ANNUAL_INCOME_RS" in input_df.columns:
        input_df["EMI_TO_INCOME_RATIO"] = input_df["MONTHLY_EMI_RS"] / annual_income

    if "LOAN_AMOUNT_RS" in input_df.columns and "ANNUAL_INCOME_RS" in input_df.columns:
        input_df["LOAN_TO_INCOME_RATIO"] = input_df["LOAN_AMOUNT_RS"] / annual_income

    family_size = input_df.get("FAMILY_SIZE", pd.Series([1])).fillna(1).replace(0, 1)
    if "ANNUAL_INCOME_RS" in input_df.columns:
        input_df["INCOME_PER_DEPENDENT"] = input_df["ANNUAL_INCOME_RS"] / family_size

    # ── Binary flag features ───────────────────────────────────────────────────
    if "EMI_TO_INCOME_RATIO" in input_df.columns:
        input_df["HIGH_EMI_BURDEN_FLAG"] = (input_df["EMI_TO_INCOME_RATIO"] > 0.5).astype(int)

    if "AGE_YEARS" in input_df.columns:
        input_df["YOUNG_BORROWER_FLAG"] = (input_df["AGE_YEARS"] < 25).astype(int)

    if "EMPLOYMENT_YEARS" in input_df.columns:
        input_df["NEW_EMPLOYEE_FLAG"] = (input_df["EMPLOYMENT_YEARS"] < 1).astype(int)

    if "OWNS_PROPERTY" in input_df.columns:
        input_df["NO_PROPERTY_FLAG"] = (input_df["OWNS_PROPERTY"].isin(["N", 0, "0"])).astype(int)

    if "CITY_TIER" in input_df.columns:
        input_df["RURAL_BORROWER_FLAG"] = (input_df["CITY_TIER"] == 3).astype(int)

    # ── Fill missing columns with 0 ────────────────────────────────────────────
    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # ── Encode any remaining string/object columns as 0 ───────────────────────
    for col in input_df.select_dtypes(include=["object"]).columns:
        input_df[col] = 0

    # ── Select and order exactly as training ──────────────────────────────────
    input_df = input_df[feature_columns]

    logger.debug(f"Preprocessed input shape: {input_df.shape}")
    return input_df


def determine_scoring_path(applicant_data: dict) -> str:
    """
    Routing logic (mirrors unified_credit_assessment from the notebook):
      - BANKED           → has CIBIL score, bureau history, or previous loan applications
      - UNBANKED_ML      → has income info but no credit history
      - ALTERNATIVE_DATA → no income info, but has UPI/alternative signals
    """
    g = applicant_data.get

    has_cibil      = float(g("CIBIL_SCORE_SOURCE_2", 0) or 0) > 0
    has_bureau     = g("HAS_BUREAU_NPA_HISTORY", -1) != -1
    has_prev_loans = int(g("TOTAL_PREV_APPLICATIONS", 0) or 0) > 0
    has_income     = float(g("ANNUAL_INCOME_RS", 0) or 0) > 0
    has_alt_data   = int(g("upi_transactions_per_month", 0) or 0) > 0

    is_banked          = has_cibil or has_bureau or has_prev_loans
    is_semi_unbanked   = has_income and not is_banked
    is_truly_unbanked  = not is_banked and not has_income and has_alt_data

    if is_banked:
        return "BANKED"
    elif is_semi_unbanked:
        return "UNBANKED_ML"
    elif is_truly_unbanked:
        return "ALTERNATIVE_DATA"
    else:
        # Default: try banked model with whatever data is available
        return "BANKED"