# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
DPIA (Data Protection Impact Assessment / RIPD) automation endpoint.
Generates full RIPD reports with risk assessment using local AI (Ollama).
"""

import json
import logging
import re
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from langchain_community.llms import Ollama

from src.core.pdf_report import generate_dpia_pdf

from src.core.config import Settings, get_settings
from src.core.prompts import DPIA_TEMPLATE, RISK_ASSESSMENT_TEMPLATE
from src.models.schemas import (
    DPIARequest,
    DPIAResponse,
    ErrorResponse,
    RiskLevel,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dpia", tags=["DPIA / RIPD"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from LLM output that may contain extra text."""
    text = text.strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find JSON block between curly braces
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Return fallback structure
    logger.warning("Could not parse LLM JSON output, returning raw text")
    return {"raw_output": text, "parse_error": True}


def _calculate_risk_score(risks: list[dict]) -> float:
    """Calculate overall risk score from list of identified risks."""
    if not risks:
        return 0.0

    risk_weights = {
        "critico": 1.0,
        "alto": 0.8,
        "medio": 0.5,
        "baixo": 0.2,
    }
    total = sum(risk_weights.get(r.get("nivel_risco", "baixo"), 0.2) for r in risks)
    return min(total / len(risks), 1.0)


def _score_to_risk_level(score: float, settings: Settings) -> RiskLevel:
    """Convert numeric score to RiskLevel enum."""
    if score >= settings.RISK_HIGH_THRESHOLD:
        return RiskLevel.HIGH
    if score >= settings.RISK_MEDIUM_THRESHOLD:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/generate",
    response_model=DPIAResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        503: {"model": ErrorResponse, "description": "LLM service unavailable"},
    },
    summary="Gerar RIPD automatico com IA",
    description=(
        "Gera um Relatorio de Impacto a Protecao de Dados (RIPD/DPIA) completo "
        "usando IA local (Ollama). O relatorio inclui avaliacao de riscos, "
        "medidas de mitigacao e recomendacoes de conformidade LGPD."
    ),
)
async def generate_dpia(
    request: DPIARequest,
    settings: Settings = Depends(get_settings),
) -> DPIAResponse:
    """
    Generate a full LGPD DPIA/RIPD report using local AI.

    The report covers:
    - Treatment description and legal basis
    - Risk assessment for data subjects
    - Mitigation measures
    - Compliance recommendations
    - Whether prior ANPD consultation is required
    """
    logger.info(
        "DPIA generation requested",
        extra={
            "company": request.company_name,
            "treatment": request.treatment_description[:100],
        },
    )

    try:
        llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )

        # Format prompt with request data
        prompt = DPIA_TEMPLATE.format(
            treatment_description=request.treatment_description,
            data_types=", ".join(request.data_types) if request.data_types else "Nao especificado",
            purposes=", ".join(request.purposes) if request.purposes else "Nao especificado",
            company_info=(
                f"Empresa: {request.company_name or 'Nao informada'}, "
                f"Setor: {request.industry_sector or 'Nao informado'}"
            ),
        )

        logger.debug("Sending DPIA prompt to Ollama model: %s", settings.OLLAMA_MODEL)
        llm_output = await llm.ainvoke(prompt)

    except Exception as exc:
        logger.error("Ollama request failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM service unavailable: {exc}. Ensure Ollama is running at {settings.OLLAMA_BASE_URL}",
        ) from exc

    # Parse LLM output
    parsed = _extract_json(str(llm_output))
    ripd_data = parsed.get("ripd", parsed)

    # Calculate risk score from identified risks
    risks = ripd_data.get("avaliacao_riscos", [])
    risk_score = _calculate_risk_score(risks)
    risk_level = _score_to_risk_level(risk_score, settings)

    # Extract compliance info
    conformidade = ripd_data.get("conformidade", {})

    return DPIAResponse(
        company_name=request.company_name or "Nao informada",
        treatment_description=request.treatment_description,
        legal_basis=ripd_data.get("descricao_tratamento", {}).get("base_legal", "Nao identificada"),
        applicable_articles=ripd_data.get("descricao_tratamento", {}).get("artigos_aplicaveis", []),
        risks=risks,
        mitigation_measures=ripd_data.get("medidas_mitigacao", []),
        overall_risk_score=risk_score,
        risk_level=risk_level,
        compliance_score=conformidade.get("score_conformidade", 0),
        recommendations=conformidade.get("recomendacoes", []),
        requires_anpd_consultation=conformidade.get("consulta_previa_anpd", False),
        anpd_consultation_reason=conformidade.get("justificativa_consulta"),
        generated_at=datetime.utcnow(),
        model_used=settings.OLLAMA_MODEL,
        raw_llm_output=str(llm_output) if settings.DEBUG else None,
    )


@router.post(
    "/generate/pdf",
    summary="Gerar RIPD em PDF",
    description="Gera o RIPD completo e retorna diretamente como arquivo PDF para download.",
    response_class=Response,
    responses={
        200: {"content": {"application/pdf": {}}, "description": "PDF do RIPD"},
        503: {"model": ErrorResponse, "description": "LLM service unavailable"},
    },
)
async def generate_dpia_pdf_endpoint(
    request: DPIARequest,
    settings: Settings = Depends(get_settings),
) -> Response:
    """Generate a full DPIA report and return it as a downloadable PDF."""
    # Reuse the JSON generation logic
    dpia_response = await generate_dpia(request, settings)
    dpia_dict = dpia_response.model_dump()

    pdf_bytes = generate_dpia_pdf(dpia_dict)

    company_slug = (request.company_name or "empresa").replace(" ", "_").lower()
    filename = f"RIPD_{company_slug}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/risk-assessment",
    summary="Avaliacao rapida de risco LGPD",
    description="Avaliacao rapida de risco de conformidade LGPD sem gerar RIPD completo.",
)
async def quick_risk_assessment(
    data_summary: str,
    security_measures: str = "Nao informadas",
    incidents_history: str = "Sem incidentes registrados",
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Quick LGPD risk assessment without full DPIA report generation."""
    try:
        llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )
        prompt = RISK_ASSESSMENT_TEMPLATE.format(
            data_summary=data_summary,
            security_measures=security_measures,
            incidents_history=incidents_history,
        )
        output = await llm.ainvoke(prompt)
        result = _extract_json(str(output))
        result["generated_at"] = datetime.utcnow().isoformat()
        result["model_used"] = settings.OLLAMA_MODEL
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
