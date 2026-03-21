# LGPD Sentinel AI - Healthcheck Tests
# Apache 2.0 License

"""Tests for the healthcheck scheduler and API endpoints."""

import json
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.core.database import (
    get_latest_health_check,
    init_db,
    list_health_checks,
    prune_health_checks,
    save_health_check,
)
from src.core.healthcheck import (
    check_database,
    check_disk,
    run_healthcheck,
)


@pytest.fixture(autouse=True)
def ensure_db():
    """Ensure the database is initialized for endpoint tests."""
    init_db()


# ---------------------------------------------------------------------------
# Database function tests
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return db_path


def test_save_and_list_health_checks(tmp_db):
    """Test saving and listing healthcheck results."""
    hc_id = save_health_check(
        overall_status="healthy",
        api_ok=True,
        ollama_ok=True,
        database_ok=True,
        disk_ok=True,
        endpoints_ok=True,
        details={"api": {"status_code": 200}},
        duration_ms=42,
        db_path=tmp_db,
    )
    assert hc_id is not None
    assert hc_id > 0

    results = list_health_checks(limit=10, db_path=tmp_db)
    assert len(results) == 1
    assert results[0]["overall_status"] == "healthy"
    assert results[0]["api_ok"] == 1
    assert results[0]["details"]["api"]["status_code"] == 200


def test_get_latest_health_check_empty(tmp_db):
    """Test that get_latest returns None when no checks exist."""
    result = get_latest_health_check(db_path=tmp_db)
    assert result is None


def test_get_latest_health_check(tmp_db):
    """Test getting the most recent healthcheck."""
    save_health_check("unhealthy", False, False, True, True, False, {}, 10, db_path=tmp_db)
    save_health_check("healthy", True, True, True, True, True, {"note": "ok"}, 20, db_path=tmp_db)

    result = get_latest_health_check(db_path=tmp_db)
    assert result is not None
    assert result["overall_status"] == "healthy"
    assert result["duration_ms"] == 20


def test_prune_health_checks(tmp_db):
    """Test pruning old healthcheck results."""
    # Insert a record with a very old timestamp
    with sqlite3.connect(tmp_db) as conn:
        conn.execute(
            """
            INSERT INTO health_checks
                (check_time, overall_status, api_ok, ollama_ok, database_ok, disk_ok, endpoints_ok, details_json, duration_ms)
            VALUES ('2020-01-01T00:00:00Z', 'healthy', 1, 1, 1, 1, 1, '{}', 10)
            """
        )
    # Insert a recent record
    save_health_check("healthy", True, True, True, True, True, {}, 10, db_path=tmp_db)

    deleted = prune_health_checks(days=30, db_path=tmp_db)
    assert deleted == 1

    remaining = list_health_checks(limit=10, db_path=tmp_db)
    assert len(remaining) == 1


# ---------------------------------------------------------------------------
# Individual check tests
# ---------------------------------------------------------------------------


def test_check_database(tmp_db):
    """Test database check against an initialized database."""
    with patch("src.core.healthcheck.DB_PATH", tmp_db):
        ok, detail = check_database()
        assert isinstance(ok, bool)
        assert ok is True
        assert "tables_found" in detail
        assert "health_checks" in detail["tables_found"]


def test_check_disk():
    """Test disk check returns sensible values."""
    ok, detail = check_disk()
    assert isinstance(ok, bool)
    assert "free_gb" in detail
    assert detail["free_gb"] >= 0


def test_check_disk_low_space():
    """Test disk check warns when free space is below threshold."""
    fake_usage = MagicMock()
    fake_usage.total = 100 * 1024 ** 3  # 100 GB
    fake_usage.used = 99.5 * 1024 ** 3  # 99.5 GB
    fake_usage.free = 0.5 * 1024 ** 3   # 0.5 GB

    with patch("src.core.healthcheck.shutil.disk_usage", return_value=fake_usage):
        ok, detail = check_disk()
        assert ok is False
        assert detail["free_gb"] == 0.5


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_healthcheck_run(client):
    """POST /healthcheck/run executes and returns a result."""
    resp = await client.post("/api/v1/healthcheck/run")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_status" in data
    assert data["overall_status"] in ("healthy", "degraded", "unhealthy")
    assert "checks" in data
    assert "duration_ms" in data


@pytest.mark.anyio
async def test_healthcheck_history_after_run(client):
    """GET /healthcheck/history returns results after a run."""
    # Run a check first
    await client.post("/api/v1/healthcheck/run")
    resp = await client.get("/api/v1/healthcheck/history")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.anyio
async def test_healthcheck_latest_after_run(client):
    """GET /healthcheck/latest returns result after a run."""
    await client.post("/api/v1/healthcheck/run")
    resp = await client.get("/api/v1/healthcheck/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_status" in data
    assert "details" in data


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------


def test_scheduler_disabled():
    """Verify scheduler does not start when disabled."""
    with patch("src.core.healthcheck.settings") as mock_settings:
        mock_settings.HEALTHCHECK_ENABLED = False
        from src.core.healthcheck import start_scheduler, scheduler
        start_scheduler()
        assert not scheduler.running
