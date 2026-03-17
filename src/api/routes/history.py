# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Audit history endpoints — list and retrieve past mapping/DPIA audits.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.core.database import (
    get_dpia_audit,
    get_mapping_audit,
    list_dpia_audits,
    list_mapping_audits,
)

router = APIRouter(prefix="/history", tags=["Histórico de Auditorias"])


@router.get("/mapping", summary="Listar auditorias de mapeamento")
async def list_mapping(limit: int = 50) -> list[dict[str, Any]]:
    """Return the most recent data-mapping audits (summary, no full JSON)."""
    return list_mapping_audits(limit=limit)


@router.get("/mapping/{audit_id}", summary="Detalhes de uma auditoria de mapeamento")
async def get_mapping(audit_id: int) -> dict[str, Any]:
    audit = get_mapping_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")
    return audit


@router.get("/dpia", summary="Listar auditorias DPIA")
async def list_dpia(limit: int = 50) -> list[dict[str, Any]]:
    """Return the most recent DPIA audits (summary, no full JSON)."""
    return list_dpia_audits(limit=limit)


@router.get("/dpia/{audit_id}", summary="Detalhes de uma auditoria DPIA")
async def get_dpia(audit_id: int) -> dict[str, Any]:
    audit = get_dpia_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")
    return audit
