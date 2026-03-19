# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Public stats endpoint — mostra métricas agregadas anônimas da instância local.
Zero dados pessoais. Zero telemetria externa. 100% local.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.core.database import DB_PATH, get_conn

router = APIRouter()


def _get_aggregate_stats(db_path: Path = DB_PATH) -> dict:
    """Lê métricas agregadas do banco local. Nenhum dado pessoal."""
    stats = {
        "total_mappings": 0,
        "total_dpias": 0,
        "total_dsrs": 0,
        "total_api_keys": 0,
        "active_api_keys": 0,
        "this_month_mappings": 0,
        "this_month_dpias": 0,
        "this_month_dsrs": 0,
        "risk_distribution": {"high": 0, "medium": 0, "low": 0},
        "avg_compliance_score": None,
    }

    if not db_path.exists():
        return stats

    with get_conn(db_path) as conn:
        # Total audits
        row = conn.execute("SELECT COUNT(*) as n FROM mapping_audits").fetchone()
        stats["total_mappings"] = row["n"] if row else 0

        row = conn.execute("SELECT COUNT(*) as n FROM dpia_audits").fetchone()
        stats["total_dpias"] = row["n"] if row else 0

        # DPIA risk distribution & avg compliance
        rows = conn.execute(
            "SELECT risk_level, compliance_score FROM dpia_audits"
        ).fetchall()
        scores = []
        for r in rows:
            lvl = (r["risk_level"] or "").lower()
            if lvl in stats["risk_distribution"]:
                stats["risk_distribution"][lvl] += 1
            if r["compliance_score"] is not None:
                scores.append(r["compliance_score"])
        if scores:
            stats["avg_compliance_score"] = round(sum(scores) / len(scores), 1)

        # API keys
        row = conn.execute("SELECT COUNT(*) as n FROM api_keys").fetchone()
        stats["total_api_keys"] = row["n"] if row else 0

        row = conn.execute(
            "SELECT COUNT(*) as n FROM api_keys WHERE active = 1"
        ).fetchone()
        stats["active_api_keys"] = row["n"] if row else 0

        # This month usage (all keys combined)
        month = datetime.utcnow().strftime("%Y-%m")
        row = conn.execute(
            """
            SELECT COALESCE(SUM(mappings),0) as m,
                   COALESCE(SUM(dpias),0)    as d,
                   COALESCE(SUM(dsrs),0)     as s
            FROM usage_monthly WHERE month = ?
            """,
            (month,),
        ).fetchone()
        if row:
            stats["this_month_mappings"] = row["m"]
            stats["this_month_dpias"] = row["d"]
            stats["this_month_dsrs"] = row["s"]

        # DSR count from usage_monthly totals
        row = conn.execute(
            "SELECT COALESCE(SUM(dsrs),0) as n FROM usage_monthly"
        ).fetchone()
        stats["total_dsrs"] = row["n"] if row else 0

    return stats


@router.get(
    "/stats",
    summary="Estatísticas públicas da instância",
    description="""
Retorna métricas agregadas anônimas desta instância do LGPD Sentinel AI.

**Nenhum dado pessoal é exposto.** Apenas contagens e distribuições.

Use isso para monitorar o uso da sua instalação.
Compartilhe com a comunidade: https://github.com/ldsjunior-ui/lgpd-sentinel-ai/discussions
    """,
    tags=["Sistema"],
)
async def public_stats():
    """Métricas agregadas públicas — zero dados pessoais."""
    stats = _get_aggregate_stats()
    return JSONResponse(
        content={
            "instance": "lgpd-sentinel-ai",
            "version": "0.1.0",
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stats": stats,
            "community": {
                "github": "https://github.com/ldsjunior-ui/lgpd-sentinel-ai",
                "discussions": "https://github.com/ldsjunior-ui/lgpd-sentinel-ai/discussions",
                "sponsor": "https://github.com/sponsors/ldsjunior-ui",
            },
            "note": "Dados 100% locais. Zero telemetria externa. Apache 2.0.",
        }
    )
