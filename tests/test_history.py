# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Unit tests for history endpoints (src/api/routes/history.py).
Uses a temporary in-memory SQLite DB — no persistent state.
"""

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.core.database import init_db, save_mapping_audit, save_dpia_audit
import tempfile
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def tmp_db(tmp_path):
    """Create a fresh temporary SQLite DB for each test."""
    db_file = tmp_path / "test_sentinel.db"
    init_db(db_path=db_file)
    return db_file


# ---------------------------------------------------------------------------
# GET /api/v1/history/mapping
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_mapping_empty(tmp_db):
    with patch("src.core.database.DB_PATH", tmp_db), \
         patch("src.api.routes.history.list_mapping_audits", return_value=[]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/history/mapping")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_history_mapping_returns_list(tmp_db):
    mock_audits = [
        {"id": 1, "company": "Empresa A", "context": "CRM", "created_at": "2026-03-17T10:00:00"},
        {"id": 2, "company": "Empresa B", "context": "RH", "created_at": "2026-03-17T11:00:00"},
    ]
    with patch("src.api.routes.history.list_mapping_audits", return_value=mock_audits):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/history/mapping")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["company"] == "Empresa A"


@pytest.mark.asyncio
async def test_history_mapping_detail_not_found():
    with patch("src.api.routes.history.get_mapping_audit", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/history/mapping/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_history_mapping_detail_found():
    mock_audit = {
        "id": 1,
        "company": "Empresa A",
        "context": "CRM",
        "items": [{"key": "email", "value": "x@x.com"}],
        "result": {"compliance_score": 80},
        "created_at": "2026-03-17T10:00:00",
    }
    with patch("src.api.routes.history.get_mapping_audit", return_value=mock_audit):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/history/mapping/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


# ---------------------------------------------------------------------------
# GET /api/v1/history/dpia
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_dpia_empty():
    with patch("src.api.routes.history.list_dpia_audits", return_value=[]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/history/dpia")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_history_dpia_returns_list():
    mock_dpias = [
        {
            "id": 1,
            "company": "Clínica X",
            "treatment": "Prontuários médicos",
            "risk_level": "high",
            "compliance_score": 65.0,
            "created_at": "2026-03-17T10:00:00",
        }
    ]
    with patch("src.api.routes.history.list_dpia_audits", return_value=mock_dpias):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/history/dpia")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["risk_level"] == "high"


@pytest.mark.asyncio
async def test_history_dpia_detail_not_found():
    with patch("src.api.routes.history.get_dpia_audit", return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/history/dpia/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_history_dpia_detail_found():
    mock_dpia = {
        "id": 1,
        "company": "Clínica X",
        "treatment": "Prontuários médicos",
        "risk_level": "high",
        "compliance_score": 65.0,
        "result": {"risks_identified": ["Dado sensível sem criptografia"]},
        "created_at": "2026-03-17T10:00:00",
    }
    with patch("src.api.routes.history.get_dpia_audit", return_value=mock_dpia):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/history/dpia/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["compliance_score"] == 65.0
