# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Healthcheck API routes — historico, ultimo resultado e execucao on-demand.
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from src.core.database import get_latest_health_check, list_health_checks
from src.core.healthcheck import run_healthcheck

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@router.get(
    "/latest",
    summary="Ultimo resultado de healthcheck",
    description="Retorna o resultado mais recente do healthcheck automatico.",
)
async def healthcheck_latest() -> dict[str, Any]:
    """Return the most recent healthcheck result."""
    result = get_latest_health_check()
    if not result:
        raise HTTPException(status_code=404, detail="Nenhum healthcheck executado ainda")
    return result


@router.get(
    "/history",
    summary="Historico de healthchecks",
    description="Retorna os resultados recentes dos healthchecks automaticos.",
)
async def healthcheck_history(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent healthcheck results."""
    return list_health_checks(limit=limit)


@router.post(
    "/run",
    summary="Executar healthcheck agora",
    description="Dispara um healthcheck imediato e retorna o resultado.",
)
async def healthcheck_run_now() -> dict[str, Any]:
    """Trigger an immediate healthcheck and return results."""
    return await run_healthcheck()
