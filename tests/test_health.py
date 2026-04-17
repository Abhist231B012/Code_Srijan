"""
tests/test_health.py

Tests for GET /api/v1/health
Verifies:
  - API is reachable
  - All 3 ML models are loaded and healthy
  - Response shape is correct
  - No auth required for health checks (used by load balancers)
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


# ── Fixture ────────────────────────────────────────────────────────────────────

@pytest.fixture
async def client():
    """Unauthenticated client — health endpoint must be public."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def auth_client():
    """Authenticated client for protected health details endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": "test-api-key"},
    ) as ac:
        yield ac


# ── Basic Health ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_returns_200(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_json(client):
    response = await client.get("/api/v1/health")
    assert response.headers["content-type"].startswith("application/json")


@pytest.mark.asyncio
async def test_health_status_ok(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_has_required_fields(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    required = ["status", "models_loaded", "version"]
    for field in required:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_health_no_auth_required(client):
    """
    Health endpoint must NOT require API key.
    Load balancers and container orchestrators (K8s) ping this without auth.
    """
    response = await client.get("/api/v1/health")
    assert response.status_code != 401
    assert response.status_code != 403


# ── Model Status ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_banked_model_loaded(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["models_loaded"]["banked_model"] is True


@pytest.mark.asyncio
async def test_health_unbanked_model_loaded(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["models_loaded"]["unbanked_model"] is True


@pytest.mark.asyncio
async def test_health_alternative_engine_loaded(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["models_loaded"]["alternative_engine"] is True


@pytest.mark.asyncio
async def test_health_shap_explainers_loaded(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["models_loaded"]["shap_explainer_banked"] is True
    assert data["models_loaded"]["shap_explainer_unbanked"] is True


@pytest.mark.asyncio
async def test_health_all_models_true(client):
    """If any model fails to load at startup, the app should refuse to serve."""
    response = await client.get("/api/v1/health")
    data = response.json()
    for model_name, loaded in data["models_loaded"].items():
        assert loaded is True, f"Model not loaded: {model_name}"


# ── Version ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_version_is_string(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0


@pytest.mark.asyncio
async def test_health_version_format(client):
    """Version should follow semver format like 1.0.0"""
    import re
    response = await client.get("/api/v1/health")
    data = response.json()
    semver_pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(semver_pattern, data["version"]), \
        f"Version '{data['version']}' does not match semver format"


# ── Detailed Health (authenticated) ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_detailed_returns_200(auth_client):
    response = await auth_client.get("/api/v1/health/detailed")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_detailed_has_uptime(auth_client):
    response = await auth_client.get("/api/v1/health/detailed")
    data = response.json()
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0


@pytest.mark.asyncio
async def test_health_detailed_has_feature_counts(auth_client):
    response = await auth_client.get("/api/v1/health/detailed")
    data = response.json()
    assert "feature_counts" in data
    assert "banked" in data["feature_counts"]
    assert "unbanked" in data["feature_counts"]


@pytest.mark.asyncio
async def test_health_detailed_requires_auth():
    """Detailed health info is sensitive — must require API key."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get("/api/v1/health/detailed")
    assert response.status_code == 401
