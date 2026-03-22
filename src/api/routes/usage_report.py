# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Usage report endpoint — relatório de uso e adoção do sistema.
Mostra quantas pessoas estão utilizando e métricas de adoção.
"""

from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.core.database import get_usage_report

router = APIRouter()


@router.get(
    "/usage-report",
    summary="Relatório de uso e adoção do sistema",
    description="""
Retorna relatório completo de uso do LGPD Sentinel AI:

- **Usuários**: total, ativos, por plano (free/trial/pro)
- **Operações**: total de mapeamentos, DPIAs e DSRs realizados
- **Tendência mensal**: uso mês a mês (últimos 12 meses)
- **Registros**: novos usuários por mês
- **Detalhamento por usuário**: uso individual (sem expor dados sensíveis)

Dados 100% locais. Nenhum dado pessoal completo é exposto.
    """,
    tags=["Sistema"],
)
async def usage_report():
    """Relatório de uso e adoção do sistema."""
    report = get_usage_report()
    return JSONResponse(
        content={
            "instance": "lgpd-sentinel-ai",
            "report_type": "usage_report",
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": {
                "total_users": report["total_users"],
                "active_users": report["active_users"],
                "free_users": report["free_users"],
                "pro_users": report["pro_users"],
                "trial_users": report["trial_users"],
                "total_operations": report["total_operations"],
                "total_mappings": report["total_mappings"],
                "total_dpias": report["total_dpias"],
                "total_dsrs": report["total_dsrs"],
            },
            "monthly_usage": report["monthly_usage"],
            "registrations_per_month": report["registrations_per_month"],
            "users_detail": report["users_detail"],
        }
    )
