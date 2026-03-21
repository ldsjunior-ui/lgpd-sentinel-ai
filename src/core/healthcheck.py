# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Healthcheck scheduler — verifica a cada 15 min se todos os servicos
oferecidos na landing page estao realmente funcionando.

Checks: API, Ollama/LLM, Database, Disco, Endpoints criticos.
"""

import logging
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.config import get_settings
from src.core.database import (
    DB_PATH,
    get_conn,
    prune_health_checks,
    save_health_check,
)

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler()

API_BASE_URL = "http://localhost:8000"


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


async def check_api() -> tuple[bool, dict[str, Any]]:
    """Check if the API /health endpoint responds correctly."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{API_BASE_URL}/health")
            data = resp.json()
            ok = resp.status_code == 200 and data.get("status") == "healthy"
            return ok, {"status_code": resp.status_code, "response": data}
    except Exception as exc:
        return False, {"error": str(exc)}


async def check_ollama() -> tuple[bool, dict[str, Any]]:
    """Check if Ollama is available and the configured model is loaded."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code != 200:
                return False, {"status_code": resp.status_code, "error": "Ollama nao respondeu"}
            data = resp.json()
            models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
            model_found = settings.OLLAMA_MODEL in models
            return model_found, {
                "status_code": 200,
                "models_available": models,
                "expected_model": settings.OLLAMA_MODEL,
                "model_found": model_found,
            }
    except Exception as exc:
        return False, {"error": str(exc)}


def check_database() -> tuple[bool, dict[str, Any]]:
    """Check database connectivity and table integrity."""
    try:
        with get_conn(DB_PATH) as conn:
            conn.execute("SELECT 1").fetchone()
            # Verify all expected tables exist
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            tables = {r["name"] for r in rows}
            expected = {"mapping_audits", "dpia_audits", "api_keys", "usage_monthly", "health_checks"}
            missing = expected - tables
            ok = len(missing) == 0
            return ok, {
                "tables_found": sorted(tables),
                "missing_tables": sorted(missing) if missing else [],
            }
    except Exception as exc:
        return False, {"error": str(exc)}


def check_disk() -> tuple[bool, dict[str, Any]]:
    """Check disk space on the reports directory."""
    try:
        reports_dir = Path(settings.REPORTS_DIR)
        reports_dir.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(str(reports_dir))
        free_gb = round(usage.free / (1024 ** 3), 2)
        total_gb = round(usage.total / (1024 ** 3), 2)
        used_gb = round(usage.used / (1024 ** 3), 2)
        ok = free_gb >= settings.HEALTHCHECK_DISK_WARNING_GB
        return ok, {
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb,
            "warning_threshold_gb": settings.HEALTHCHECK_DISK_WARNING_GB,
        }
    except Exception as exc:
        return False, {"error": str(exc)}


async def check_endpoints() -> tuple[bool, dict[str, Any]]:
    """Check that critical GET endpoints respond with 200."""
    endpoints = [
        "/api/v1/stats",
        "/api/v1/dsr/types",
    ]
    results = {}
    all_ok = True
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            for ep in endpoints:
                try:
                    resp = await client.get(f"{API_BASE_URL}{ep}")
                    ok = resp.status_code == 200
                    results[ep] = {"status_code": resp.status_code, "ok": ok}
                    if not ok:
                        all_ok = False
                except Exception as exc:
                    results[ep] = {"error": str(exc), "ok": False}
                    all_ok = False
    except Exception as exc:
        return False, {"error": str(exc)}
    return all_ok, results


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


async def run_healthcheck() -> dict[str, Any]:
    """Execute all healthchecks, save to DB, return result dict."""
    start = time.monotonic()

    api_ok, api_detail = await check_api()
    ollama_ok, ollama_detail = await check_ollama()
    db_ok, db_detail = check_database()
    disk_ok, disk_detail = check_disk()
    endpoints_ok, endpoints_detail = await check_endpoints()

    duration_ms = int((time.monotonic() - start) * 1000)

    checks = [api_ok, ollama_ok, db_ok, disk_ok, endpoints_ok]
    if all(checks):
        overall = "healthy"
    elif any(checks):
        overall = "degraded"
    else:
        overall = "unhealthy"

    details = {
        "api": api_detail,
        "ollama": ollama_detail,
        "database": db_detail,
        "disk": disk_detail,
        "endpoints": endpoints_detail,
    }

    try:
        save_health_check(
            overall_status=overall,
            api_ok=api_ok,
            ollama_ok=ollama_ok,
            database_ok=db_ok,
            disk_ok=disk_ok,
            endpoints_ok=endpoints_ok,
            details=details,
            duration_ms=duration_ms,
        )
        prune_health_checks(days=settings.HEALTHCHECK_HISTORY_DAYS)
    except Exception as exc:
        logger.error("Failed to save healthcheck result: %s", exc)

    logger.info(
        "Healthcheck completed: %s (api=%s ollama=%s db=%s disk=%s endpoints=%s) %dms",
        overall, api_ok, ollama_ok, db_ok, disk_ok, endpoints_ok, duration_ms,
    )

    return {
        "overall_status": overall,
        "checks": details,
        "duration_ms": duration_ms,
    }


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------


def start_scheduler() -> None:
    """Configure and start the healthcheck scheduler."""
    if not settings.HEALTHCHECK_ENABLED:
        logger.info("Healthcheck scheduler disabled via HEALTHCHECK_ENABLED=false")
        return

    scheduler.add_job(
        run_healthcheck,
        trigger="interval",
        minutes=settings.HEALTHCHECK_INTERVAL_MINUTES,
        id="healthcheck",
        replace_existing=True,
        # Small delay on first run to let uvicorn finish binding
        next_run_time=datetime.utcnow() + timedelta(seconds=10),
    )
    scheduler.start()
    logger.info(
        "Healthcheck scheduler started (interval=%d min)",
        settings.HEALTHCHECK_INTERVAL_MINUTES,
    )


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Healthcheck scheduler stopped")
