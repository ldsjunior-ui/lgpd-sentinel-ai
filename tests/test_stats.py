# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Unit tests for the public stats endpoint (src/api/routes/stats.py).
Uses temporary SQLite DB — no persistent state required.
"""


import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.core.database import init_db, save_mapping_audit, save_dpia_audit
from src.api.routes.stats import _get_aggregate_stats


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    """Fresh SQLite DB per test."""
    db_file = tmp_path / "test_stats.db"
    init_db(db_path=db_file)
    return db_file


# ---------------------------------------------------------------------------
# Unit: _get_aggregate_stats()
# ---------------------------------------------------------------------------


def test_stats_empty_db(tmp_db):
    """Stats on a fresh DB should return all zeros."""
    stats = _get_aggregate_stats(db_path=tmp_db)
    assert stats["total_mappings"] == 0
    assert stats["total_dpias"] == 0
    assert stats["total_dsrs"] == 0
    assert stats["total_api_keys"] == 0
    assert stats["avg_compliance_score"] is None


def test_stats_missing_db(tmp_path):
    """Stats on non-existent DB should not crash — returns zeros."""
    fake_path = tmp_path / "nonexistent.db"
    stats = _get_aggregate_stats(db_path=fake_path)
    assert stats["total_mappings"] == 0
    assert stats["total_dpias"] == 0


def test_stats_counts_mapping_audits(tmp_db):
    """After saving mapping audits the count should reflect them."""
    save_mapping_audit(
        company="Empresa A",
        context="CRM",
        items=[{"key": "email", "value": "a@b.com"}],
        result={"compliance_score": 80},
        db_path=tmp_db,
    )
    save_mapping_audit(
        company="Empresa B",
        context="RH",
        items=[{"key": "cpf", "value": "123.456.789-00"}],
        result={"compliance_score": 70},
        db_path=tmp_db,
    )
    stats = _get_aggregate_stats(db_path=tmp_db)
    assert stats["total_mappings"] == 2


def test_stats_counts_dpia_audits(tmp_db):
    """After saving DPIA audits, risk distribution should be populated."""
    save_dpia_audit(
        company="Clínica X",
        treatment="Prontuários médicos",
        risk_level="high",
        compliance_score=60.0,
        result={},
        db_path=tmp_db,
    )
    save_dpia_audit(
        company="Loja Y",
        treatment="Dados de compra",
        risk_level="low",
        compliance_score=90.0,
        result={},
        db_path=tmp_db,
    )
    stats = _get_aggregate_stats(db_path=tmp_db)
    assert stats["total_dpias"] == 2
    assert stats["risk_distribution"]["high"] == 1
    assert stats["risk_distribution"]["low"] == 1
    assert stats["avg_compliance_score"] == 75.0


# ---------------------------------------------------------------------------
# Integration: GET /api/v1/stats (via FastAPI test client)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stats_endpoint_returns_200():
    """GET /api/v1/stats should return 200 with the expected structure."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/stats")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_stats_endpoint_response_structure():
    """Response must have all required top-level keys."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/stats")

    data = response.json()
    assert data["instance"] == "lgpd-sentinel-ai"
    assert "version" in data
    assert "generated_at" in data
    assert "stats" in data
    assert "community" in data
    assert "note" in data


@pytest.mark.asyncio
async def test_stats_endpoint_stats_fields():
    """All expected stats fields must be present."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/stats")

    stats = response.json()["stats"]
    required_keys = [
        "total_mappings",
        "total_dpias",
        "total_dsrs",
        "total_api_keys",
        "active_api_keys",
        "this_month_mappings",
        "this_month_dpias",
        "this_month_dsrs",
        "risk_distribution",
        "avg_compliance_score",
    ]
    for key in required_keys:
        assert key in stats, f"Missing stats field: {key}"


@pytest.mark.asyncio
async def test_stats_endpoint_community_links():
    """Community section must contain expected URLs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/stats")

    community = response.json()["community"]
    assert "github" in community
    assert "discussions" in community
    assert "sponsor" in community
    assert "github.com" in community["github"]


@pytest.mark.asyncio
async def test_stats_endpoint_no_auth_required():
    """Stats endpoint must be publicly accessible — no X-API-Key needed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/stats")

    # Must NOT return 401 or 403
    assert response.status_code not in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )
