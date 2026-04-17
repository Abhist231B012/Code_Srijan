"""
tests/test_predict.py

Tests for POST /api/v1/predict
Covers all 3 scoring paths:
  - BANKED         (has CIBIL / bureau history)
  - UNBANKED_ML    (no bureau, has income/employment data)
  - ALTERNATIVE    (truly unbanked — UPI / utility / mobile data only)
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def banked_payload():
    """Applicant with full bureau and CIBIL history."""
    return {
        "ANNUAL_INCOME_RS": 600000,
        "LOAN_AMOUNT_RS": 250000,
        "MONTHLY_EMI_RS": 10000,
        "AGE_YEARS": 35,
        "EMPLOYMENT_YEARS": 6.0,
        "CIBIL_SCORE_SOURCE_2": 0.70,
        "HAS_BUREAU_NPA_HISTORY": 0,
        "TOTAL_PREV_APPLICATIONS": 3,
        "PREV_APPROVAL_RATE": 0.85,
        "CITY_TIER": 2,
        "OWNS_PROPERTY": "Y",
    }


@pytest.fixture
def unbanked_ml_payload():
    """Applicant with income/employment data but no bureau history."""
    return {
        "ANNUAL_INCOME_RS": 200000,
        "LOAN_AMOUNT_RS": 80000,
        "MONTHLY_EMI_RS": 4000,
        "AGE_YEARS": 28,
        "EMPLOYMENT_YEARS": 2.5,
        "EMPLOYMENT_TYPE": "Private_Salaried",
        "CITY_TIER": 2,
        "OWNS_PROPERTY": "N",
        "HAS_MOBILE": 1,
        "MOBILE_STABLE_FLAG": 1,
    }


@pytest.fixture
def alternative_payload():
    """Truly unbanked applicant — alternative data only."""
    return {
        "upi_transactions_per_month": 35,
        "avg_upi_amount_rs": 1800,
        "utility_bills_paid": 10,
        "total_utility_bills": 12,
        "types_of_bills": 2,
        "mobile_years_active": 3.5,
        "same_number": 1,
        "prepaid_or_postpaid": "postpaid",
        "monthly_income_rs": 22000,
        "employment_type": "Self_Employed_Business",
        "employment_years": 4.0,
        "has_aadhaar": 1,
        "has_pan": 1,
        "has_bank_statement": 0,
        "rent_paid_months": 11,
        "total_months_rented": 12,
        "age_years": 33,
        "number_of_dependents": 2,
        "city_tier": 2,
        "education_level": "Higher_Secondary_12th",
    }


@pytest.fixture
def high_risk_payload():
    """High-risk applicant — should receive REJECT decision."""
    return {
        "ANNUAL_INCOME_RS": 80000,
        "LOAN_AMOUNT_RS": 500000,
        "MONTHLY_EMI_RS": 40000,
        "AGE_YEARS": 22,
        "EMPLOYMENT_YEARS": 0.3,
        "CIBIL_SCORE_SOURCE_2": 0.10,
        "HAS_BUREAU_NPA_HISTORY": 1,
        "TOTAL_PREV_APPLICATIONS": 5,
        "PREV_APPROVAL_RATE": 0.1,
        "CITY_TIER": 3,
    }


# ── Helper ─────────────────────────────────────────────────────────────────────

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": "test-api-key"},
    ) as ac:
        yield ac


# ── PATH 1: Banked ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_banked_returns_200(client, banked_payload):
    response = await client.post("/api/v1/predict", json=banked_payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_predict_banked_scoring_path(client, banked_payload):
    response = await client.post("/api/v1/predict", json=banked_payload)
    data = response.json()
    assert data["scoring_path"] == "BANKED"


@pytest.mark.asyncio
async def test_predict_banked_score_in_valid_range(client, banked_payload):
    response = await client.post("/api/v1/predict", json=banked_payload)
    data = response.json()
    assert 300 <= data["credit_score"] <= 900


@pytest.mark.asyncio
async def test_predict_banked_response_fields(client, banked_payload):
    response = await client.post("/api/v1/predict", json=banked_payload)
    data = response.json()
    required_fields = [
        "credit_score", "default_probability", "score_band",
        "npa_category", "rbi_classification", "decision",
        "max_loan_eligible_rs", "scoring_path", "reasoning",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_predict_banked_decision_values(client, banked_payload):
    response = await client.post("/api/v1/predict", json=banked_payload)
    data = response.json()
    assert data["decision"] in ("APPROVE", "CONDITIONAL", "REJECT")


@pytest.mark.asyncio
async def test_predict_banked_score_band_values(client, banked_payload):
    response = await client.post("/api/v1/predict", json=banked_payload)
    data = response.json()
    valid_bands = ("EXCELLENT", "GOOD", "FAIR", "POOR", "VERY POOR")
    assert data["score_band"] in valid_bands


# ── PATH 2: Unbanked ML ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_unbanked_ml_returns_200(client, unbanked_ml_payload):
    response = await client.post("/api/v1/predict", json=unbanked_ml_payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_predict_unbanked_ml_scoring_path(client, unbanked_ml_payload):
    response = await client.post("/api/v1/predict", json=unbanked_ml_payload)
    data = response.json()
    assert data["scoring_path"] == "UNBANKED_ML"


@pytest.mark.asyncio
async def test_predict_unbanked_ml_score_in_valid_range(client, unbanked_ml_payload):
    response = await client.post("/api/v1/predict", json=unbanked_ml_payload)
    data = response.json()
    assert 300 <= data["credit_score"] <= 900


@pytest.mark.asyncio
async def test_predict_unbanked_ml_probability_range(client, unbanked_ml_payload):
    response = await client.post("/api/v1/predict", json=unbanked_ml_payload)
    data = response.json()
    assert 0.0 <= data["default_probability"] <= 100.0


# ── PATH 3: Alternative Data ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_alternative_returns_200(client, alternative_payload):
    response = await client.post("/api/v1/predict", json=alternative_payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_predict_alternative_scoring_path(client, alternative_payload):
    response = await client.post("/api/v1/predict", json=alternative_payload)
    data = response.json()
    assert data["scoring_path"] == "ALTERNATIVE_DATA"


@pytest.mark.asyncio
async def test_predict_alternative_has_breakdown(client, alternative_payload):
    response = await client.post("/api/v1/predict", json=alternative_payload)
    data = response.json()
    assert "alternative_score_breakdown" in data


@pytest.mark.asyncio
async def test_predict_alternative_score_in_valid_range(client, alternative_payload):
    response = await client.post("/api/v1/predict", json=alternative_payload)
    data = response.json()
    assert 300 <= data["credit_score"] <= 900


# ── High Risk / Edge Cases ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_high_risk_gets_rejected(client, high_risk_payload):
    response = await client.post("/api/v1/predict", json=high_risk_payload)
    data = response.json()
    assert data["decision"] == "REJECT"


@pytest.mark.asyncio
async def test_predict_high_risk_low_score(client, high_risk_payload):
    response = await client.post("/api/v1/predict", json=high_risk_payload)
    data = response.json()
    assert data["credit_score"] < 650


@pytest.mark.asyncio
async def test_predict_empty_payload_returns_422(client):
    """Empty payload should fail Pydantic validation."""
    response = await client.post("/api/v1/predict", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_predict_missing_api_key_returns_401():
    """Request without API key should be rejected."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.post("/api/v1/predict", json={"ANNUAL_INCOME_RS": 100000})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_predict_npa_classification_values(client, banked_payload):
    response = await client.post("/api/v1/predict", json=banked_payload)
    data = response.json()
    valid_npa = (
        "Standard Asset",
        "Special Mention Account",
        "Sub-Standard NPA",
        "Doubtful NPA",
        "Loss Asset",
    )
    assert data["npa_category"] in valid_npa


@pytest.mark.asyncio
async def test_predict_reasoning_is_list(client, banked_payload):
    response = await client.post("/api/v1/predict", json=banked_payload)
    data = response.json()
    assert isinstance(data["reasoning"], list)
    assert len(data["reasoning"]) > 0
