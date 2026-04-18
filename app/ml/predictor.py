import numpy as np
from app.ml.model_loader import get_model, get_model_optional
from app.ml.preprocessor import build_feature_dataframe, determine_scoring_path
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Score helpers (exact formulas from notebook) ──────────────────────────────

def _generate_credit_score(default_probability: float) -> int:
    score = 900 - (default_probability ** 0.7) * 600
    return int(np.clip(score, 300, 900))


def _get_score_band(credit_score: int) -> tuple:
    if credit_score >= 750:
        return "EXCELLENT", "Very low risk — Premium borrower"
    elif credit_score >= 700:
        return "GOOD", "Low risk — Standard approval"
    elif credit_score >= 650:
        return "FAIR", "Moderate risk — Conditional approval"
    elif credit_score >= 600:
        return "POOR", "High risk — Requires collateral"
    else:
        return "VERY POOR", "Very high risk — Likely rejection"


def _get_npa_classification(default_probability: float) -> dict:
    p = default_probability
    if p < 0.05:
        return {"npa_category": "Standard Asset",        "rbi_classification": "SA"}
    elif p < 0.20:
        return {"npa_category": "Special Mention Account","rbi_classification": "SMA"}
    elif p < 0.50:
        return {"npa_category": "Sub-Standard NPA",      "rbi_classification": "SS-NPA"}
    elif p < 0.80:
        return {"npa_category": "Doubtful NPA",          "rbi_classification": "D-NPA"}
    else:
        return {"npa_category": "Loss Asset",            "rbi_classification": "LOSS"}


def _get_decision(credit_score: int) -> str:
    if credit_score >= 700:
        return "APPROVE"
    elif credit_score >= 550:
        return "CONDITIONAL"
    else:
        return "REJECT"


def _get_loan_terms(credit_score: int, annual_income: float, loan_amount: float) -> dict:
    if credit_score >= 750:
        rate = 8.5
        max_loan = min(annual_income * 5, loan_amount * 1.2)
    elif credit_score >= 700:
        rate = 10.5
        max_loan = min(annual_income * 4, loan_amount)
    elif credit_score >= 650:
        rate = 13.0
        max_loan = min(annual_income * 2.5, loan_amount * 0.8)
    elif credit_score >= 600:
        rate = 16.0
        max_loan = min(annual_income * 1.5, loan_amount * 0.5)
    else:
        rate = None
        max_loan = 0

    return {
        "max_loan_eligible_rs": round(max_loan, 2) if max_loan else 0,
        "interest_rate_pct": rate,
    }


def _build_reasoning(
    credit_score: int,
    default_probability: float,
    applicant_data: dict,
    decision: str,
) -> list:
    reasons = []

    if applicant_data.get("HAS_BUREAU_NPA_HISTORY") == 1:
        reasons.append("Previous NPA history detected")

    if default_probability > 0.80:
        reasons.append(f"Very high default probability: {round(default_probability * 100, 1)}%")
    elif default_probability > 0.50:
        reasons.append(f"High default probability: {round(default_probability * 100, 1)}%")

    if credit_score < 550:
        reasons.append(f"Credit score too low: {credit_score}")

    emi_ratio = applicant_data.get("EMI_TO_INCOME_RATIO") or (
        (applicant_data.get("MONTHLY_EMI_RS", 0) or 0) /
        max(applicant_data.get("ANNUAL_INCOME_RS", 1) or 1, 1)
    )
    if emi_ratio > 0.5:
        reasons.append(f"High EMI-to-income burden: {round(emi_ratio * 100, 1)}%")

    if decision == "REJECT" and len(reasons) < 2:
        reasons.append("Multiple high-risk factors")

    if decision == "APPROVE":
        reasons.append(f"Strong credit profile — score {credit_score}")

    if decision == "CONDITIONAL":
        reasons.append("Collateral or guarantor recommended")

    return reasons


def _shap_reasons(applicant_data: dict, shap_values, feature_cols: list, top_n: int = 5) -> dict:
    """Extract top SHAP risk/strength factors for the response."""
    FEATURE_LABELS = {
        "CIBIL_SCORE_SOURCE_1": "CIBIL Score (Source 1)",
        "CIBIL_SCORE_SOURCE_2": "CIBIL Score (Source 2)",
        "CIBIL_SCORE_SOURCE_3": "CIBIL Score (Source 3)",
        "HAS_BUREAU_NPA_HISTORY": "Bureau NPA History",
        "ANNUAL_INCOME_RS": "Annual Income",
        "LOAN_AMOUNT_RS": "Loan Amount",
        "MONTHLY_EMI_RS": "Monthly EMI",
        "EMI_TO_INCOME_RATIO": "EMI-to-Income Ratio",
        "LOAN_TO_INCOME_RATIO": "Loan-to-Income Ratio",
        "AGE_YEARS": "Age",
        "EMPLOYMENT_YEARS": "Employment Duration",
        "OWNS_PROPERTY": "Owns Property",
        "CITY_TIER": "City Tier",
        "OCCUPATION": "Occupation",
        "EDUCATION_LEVEL": "Education Level",
        "EMPLOYMENT_TYPE": "Employment Type",
        "AADHAAR_SUBMITTED": "Aadhaar Submitted",
        "PAN_SUBMITTED": "PAN Card Submitted",
    }

    sv = shap_values[0] if hasattr(shap_values, "__len__") and isinstance(shap_values[0], list) else shap_values
    if isinstance(sv, list):
        sv = sv[1]  # class 1 for binary

    feature_impacts = list(zip(feature_cols, sv[0] if sv.ndim == 2 else sv))
    sorted_impacts = sorted(feature_impacts, key=lambda x: abs(x[1]), reverse=True)

    risk_factors = {}
    strength_factors = {}
    for feat, impact in sorted_impacts:
        label = FEATURE_LABELS.get(feat, feat.replace("_", " ").title())
        if impact > 0 and len(risk_factors) < top_n:
            risk_factors[label] = round(float(impact), 4)
        elif impact < 0 and len(strength_factors) < top_n:
            strength_factors[label] = round(float(impact), 4)
        if len(risk_factors) >= top_n and len(strength_factors) >= top_n:
            break

    return {"risk_factors": risk_factors, "strength_factors": strength_factors}


# ── Main entry point ──────────────────────────────────────────────────────────

def unified_credit_assessment(applicant_data: dict, include_shap: bool = True) -> dict:
    """
    Full prediction pipeline.
    Routes to: BANKED → UNBANKED_ML → ALTERNATIVE_DATA
    Returns a structured response dict ready for the API.
    """
    scoring_path = determine_scoring_path(applicant_data)
    logger.info(f"Scoring path determined: {scoring_path}")

    explanation = {}

    # ── BANKED PATH ───────────────────────────────────────────────────────────
    if scoring_path == "BANKED":
        model      = get_model("model_banked")
        feat_cols  = get_model("feature_cols_banked")
        input_df   = build_feature_dataframe(applicant_data, feat_cols)
        prob       = float(model.predict_proba(input_df)[0][1])

        if include_shap:
            try:
                explainer = get_model("shap_banked")
                sv = explainer.shap_values(input_df)
                explanation = _shap_reasons(applicant_data, sv, feat_cols)
                explanation["method"] = "SHAP_TreeExplainer"
            except Exception as e:
                logger.warning(f"SHAP failed for BANKED path: {e}")
                explanation = {"method": "SHAP_UNAVAILABLE"}

    # ── UNBANKED ML PATH ──────────────────────────────────────────────────────
    elif scoring_path == "UNBANKED_ML":
        model     = get_model("model_unbanked")
        feat_cols = get_model("feature_cols_unbanked")

        # Add ratio features before preprocessing
        income = float(applicant_data.get("ANNUAL_INCOME_RS", 1) or 1)
        applicant_data["EMI_TO_INCOME_RATIO"]  = float(applicant_data.get("MONTHLY_EMI_RS", 0) or 0) / income
        applicant_data["LOAN_TO_INCOME_RATIO"] = float(applicant_data.get("LOAN_AMOUNT_RS", 0) or 0) / income

        input_df = build_feature_dataframe(applicant_data, feat_cols)
        prob     = float(model.predict_proba(input_df)[0][1])

        if include_shap:
            try:
                explainer = get_model("shap_unbanked")
                sv = explainer.shap_values(input_df)
                explanation = _shap_reasons(applicant_data, sv, feat_cols)
                explanation["method"] = "SHAP_TreeExplainer"
            except Exception as e:
                logger.warning(f"SHAP failed for UNBANKED_ML path: {e}")
                explanation = {"method": "SHAP_UNAVAILABLE"}

    # ── ALTERNATIVE DATA PATH ─────────────────────────────────────────────────
    else:
        scoring_path = "ALTERNATIVE_DATA"
        alt_engine = get_model("alt_scoring_engine")
        alt_result = alt_engine(applicant_data)

        prob       = float(alt_result.get("default_probability", 50)) / 100
        breakdown  = alt_result.get("score_breakdown", {})
        explanation = {
            "method": "RULE_BASED_ALTERNATIVE",
            "score_breakdown": breakdown,
            "risk_factors": {},
            "strength_factors": {},
        }

    # ── Common output construction ─────────────────────────────────────────────
    credit_score = _generate_credit_score(prob)
    score_band, risk_description = _get_score_band(credit_score)
    npa_info     = _get_npa_classification(prob)
    decision     = _get_decision(credit_score)
    loan_terms   = _get_loan_terms(
        credit_score,
        float(applicant_data.get("ANNUAL_INCOME_RS", 0) or 0),
        float(applicant_data.get("LOAN_AMOUNT_RS", 0) or 0),
    )
    reasoning = _build_reasoning(credit_score, prob, applicant_data, decision)

    return {
        "scoring_path":         scoring_path,
        "credit_score":         credit_score,
        "default_probability":  round(prob * 100, 2),
        "score_band":           score_band,
        "risk_description":     risk_description,
        "decision":             decision,
        "npa_category":         npa_info["npa_category"],
        "rbi_classification":   npa_info["rbi_classification"],
        "max_loan_eligible_rs": loan_terms["max_loan_eligible_rs"],
        "interest_rate_pct":    loan_terms["interest_rate_pct"],
        "reasoning":            reasoning,
        "explanation":          explanation,
    }