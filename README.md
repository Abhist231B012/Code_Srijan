# AI-Based Credit Scoring System — Backend API

A production-grade FastAPI backend for the **AI-Based Credit Scoring for the Unbanked Population** project.
Built to serve LightGBM models and an alternative data scoring engine via a REST API.

---

## What it does

Scores loan applicants using one of three paths automatically:

| Path | Who it serves | Model used |
|---|---|---|
| `BANKED` | Has CIBIL / bureau history | LightGBM Phase 1 |
| `UNBANKED_ML` | Has income data, no bureau | LightGBM Phase 2A |
| `ALTERNATIVE_DATA` | No formal data at all | Rule-based Phase 2B |

Returns a CIBIL-style score (300–900), NPA classification (RBI categories), loan decision, and SHAP-based explanation of why.

---

## Quickstart

### 1. Clone and setup environment

```bash
git clone https://github.com/your-username/credit-scoring-backend.git
cd credit-scoring-backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Add your trained model files

Copy all `.pkl` files from your notebook into the `models/` folder:

```bash
cp /path/to/notebook/*.pkl models/
```

Required files:
- `lightgbm_credit_model.pkl`
- `lightgbm_unbanked_model.pkl`
- `alternative_scoring_engine.pkl`
- `shap_explainer_banked.pkl`
- `shap_explainer_unbanked.pkl`
- `feature_columns.pkl`
- `feature_columns_unbanked.pkl`

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/credit_scoring_db
API_KEY=your-secret-api-key
APP_VERSION=1.0.0
MODEL_DIR=models/
DEBUG=False
```

### 4. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API is now live at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

---

## Run with Docker

```bash
docker-compose up --build
```

---

## API endpoints

### `POST /api/v1/predict`

Score a loan applicant. Automatically routes to the correct model.

**Headers:**
```
X-API-Key: your-secret-api-key
Content-Type: application/json
```

**Example — Banked applicant:**
```json
{
  "ANNUAL_INCOME_RS": 600000,
  "LOAN_AMOUNT_RS": 250000,
  "MONTHLY_EMI_RS": 10000,
  "AGE_YEARS": 35,
  "EMPLOYMENT_YEARS": 6.0,
  "CIBIL_SCORE_SOURCE_2": 0.70,
  "HAS_BUREAU_NPA_HISTORY": 0,
  "CITY_TIER": 2
}
```

**Example — Truly unbanked applicant (alternative data):**
```json
{
  "upi_transactions_per_month": 35,
  "avg_upi_amount_rs": 1800,
  "utility_bills_paid": 10,
  "total_utility_bills": 12,
  "mobile_years_active": 3.5,
  "monthly_income_rs": 22000,
  "has_aadhaar": 1,
  "has_pan": 1,
  "age_years": 33
}
```

**Response:**
```json
{
  "credit_score": 724,
  "default_probability": 18.4,
  "score_band": "GOOD",
  "npa_category": "Special Mention Account",
  "rbi_classification": "SMA",
  "scoring_path": "BANKED",
  "decision": "APPROVE",
  "max_loan_eligible_rs": 1680000,
  "interest_rate_pct": 10.2,
  "reasoning": [
    "Good credit profile — Score: 724",
    "Default probability low: 18.4%"
  ]
}
```

---

### `POST /api/v1/explain`

Get SHAP-based explanation for a prediction.

**Response includes:**
```json
{
  "credit_score": 724,
  "explanation_method": "SHAP_TreeExplainer",
  "risk_factors": {
    "EMI_TO_INCOME_RATIO": 0.043,
    "CREDIT_HUNGER_SCORE": 0.021
  },
  "strength_factors": {
    "CIBIL_SCORE_SOURCE_2": -0.112,
    "EMPLOYMENT_YEARS": -0.067
  },
  "formatted_report": "..."
}
```

---

### `GET /api/v1/health`

Public health check (no auth required). Used by load balancers.

```json
{
  "status": "ok",
  "version": "1.0.0",
  "models_loaded": {
    "banked_model": true,
    "unbanked_model": true,
    "alternative_engine": true,
    "shap_explainer_banked": true,
    "shap_explainer_unbanked": true
  }
}
```

---

### `GET /api/v1/health/detailed`

Requires API key. Returns uptime, feature counts, and model metadata.

---

## Run tests

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Database migrations

This project uses **Alembic** with async PostgreSQL (`asyncpg`).

```bash
# Create a new migration after changing ORM models
alembic revision --autogenerate -m "add applicant table"

# Apply migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

---

## Authentication

All endpoints except `/health` require an API key header:

```
X-API-Key: your-secret-api-key
```

Set `API_KEY` in your `.env` file.

---

## Tech stack

| Component | Technology |
|---|---|
| Web framework | FastAPI |
| ML models | LightGBM |
| Explainability | SHAP |
| Data validation | Pydantic v2 |
| Database | PostgreSQL + asyncpg |
| Migrations | Alembic (async) |
| Server | Uvicorn |
| Testing | Pytest + httpx |
| Containerization | Docker |

---

## Team

Built as part of the **AI-Based Credit Scoring for the Unbanked Population** project.
Problem statement focused on financial inclusion for underserved communities in developing regions.
