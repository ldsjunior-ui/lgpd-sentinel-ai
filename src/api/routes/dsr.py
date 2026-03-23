# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
DSR — Data Subject Rights endpoint (Direitos do Titular - Art. 18 LGPD).
Handles requests for access, correction, deletion, portability, etc.
"""

import json
import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from langchain_community.llms import Ollama
from pydantic import BaseModel, Field

from src.core.config import Settings, get_settings
from src.core.prompts import DSR_TEMPLATE
from src.core.quota import QuotaCheck

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dsr", tags=["DSR / Direitos do Titular"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class DSRType(str, Enum):
    ACCESS         = "acesso"
    CORRECTION     = "correcao"
    DELETION       = "exclusao"
    PORTABILITY    = "portabilidade"
    OPPOSITION     = "oposicao"
    REVOKE_CONSENT = "revogacao_consentimento"
    RESTRICTION    = "restricao"
    INFORMATION    = "informacao"


class DSRRequest(BaseModel):
    company_name: Optional[str] = Field(default=None, description="Nome da empresa controladora")
    request_type: DSRType = Field(..., description="Tipo de direito solicitado (Art. 18 LGPD)")
    request_description: str = Field(
        ..., min_length=10,
        description="Descricao detalhada da solicitacao do titular"
    )
    data_context: Optional[str] = Field(
        default=None,
        description="Contexto dos dados envolvidos (sistema, base, etc.)"
    )
    titular_name: Optional[str] = Field(default=None, description="Nome do titular (anonimizado)")


class DSRResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    company_name: str
    titular_name: Optional[str] = None
    request_type: DSRType
    direito_identificado: str
    artigo_lgpd: str
    pode_atender: bool
    justificativa: str
    prazo_resposta_dias: int = 15
    acoes_requeridas: list[dict[str, Any]] = Field(default_factory=list)
    resposta_ao_titular: str
    requer_dpo: bool = False
    requer_anpd: bool = False
    justificativa_anpd: Optional[str] = None
    documentacao_necessaria: list[str] = Field(default_factory=list)
    generated_at: datetime
    model_used: str


# ─── Helper ───────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"raw_output": text, "parse_error": True}


# ─── Endpoint ─────────────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=DSRResponse,
    summary="Analisar solicitacao de direito do titular (Art. 18 LGPD)",
    description=(
        "Recebe uma solicitacao de direito do titular (acesso, correcao, exclusao, "
        "portabilidade, etc.) e retorna orientacoes detalhadas, resposta ao titular "
        "e acoes necessarias, com base no Art. 18 da LGPD."
    ),
)
async def analyze_dsr(
    request: DSRRequest,
    settings: Settings = Depends(get_settings),
    _quota: dict = Depends(QuotaCheck("dsrs")),
) -> DSRResponse:
    """Analyze a Data Subject Rights request and generate response guidance."""
    logger.info(
        "DSR request received",
        extra={"type": request.request_type, "company": request.company_name},
    )

    try:
        llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.0,
            num_predict=768,
            num_ctx=2048,
        )
        prompt = DSR_TEMPLATE.format(
            request_type=request.request_type.value,
            request_description=request.request_description,
            company_name=request.company_name or "Não informada",
            data_context=request.data_context or "Não especificado",
        )
        llm_output = await llm.ainvoke(prompt)

    except Exception as exc:
        logger.error("Ollama request failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM service unavailable: {exc}",
        ) from exc

    parsed = _extract_json(str(llm_output))
    dsr_data = parsed.get("dsr", parsed)

    return DSRResponse(
        company_name=request.company_name or "Não informada",
        titular_name=request.titular_name,
        request_type=request.request_type,
        direito_identificado=dsr_data.get("direito_identificado", request.request_type.value),
        artigo_lgpd=dsr_data.get("artigo_lgpd", "Art. 18 LGPD"),
        pode_atender=dsr_data.get("pode_atender", True),
        justificativa=dsr_data.get("justificativa", ""),
        prazo_resposta_dias=dsr_data.get("prazo_resposta_dias", 15),
        acoes_requeridas=dsr_data.get("acoes_requeridas", []),
        resposta_ao_titular=dsr_data.get("resposta_ao_titular", ""),
        requer_dpo=dsr_data.get("requer_dpo", False),
        requer_anpd=dsr_data.get("requer_anpd", False),
        justificativa_anpd=dsr_data.get("justificativa_anpd"),
        documentacao_necessaria=dsr_data.get("documentacao_necessaria", []),
        generated_at=datetime.utcnow(),
        model_used=settings.OLLAMA_MODEL,
    )


@router.get(
    "/types",
    summary="Listar tipos de direitos disponíveis (Art. 18 LGPD)",
)
async def list_dsr_types() -> dict[str, Any]:
    """Return all DSR types with their LGPD legal reference."""
    return {
        "direitos": [
            {"type": t.value, "artigo": "Art. 18 LGPD", "descricao": desc}
            for t, desc in {
                DSRType.ACCESS:         "Confirmação e acesso aos dados tratados",
                DSRType.CORRECTION:     "Correção de dados incompletos, inexatos ou desatualizados",
                DSRType.DELETION:       "Eliminação de dados desnecessários ou tratados em desconformidade",
                DSRType.PORTABILITY:    "Portabilidade dos dados a outro fornecedor",
                DSRType.OPPOSITION:     "Oposição ao tratamento realizado em desconformidade",
                DSRType.REVOKE_CONSENT: "Revogação do consentimento",
                DSRType.RESTRICTION:    "Restrição do tratamento de dados",
                DSRType.INFORMATION:    "Informação sobre controladores com quem os dados são compartilhados",
            }.items()
        ],
        "prazo_legal_dias": 15,
        "base_legal": "Art. 18, §5 da Lei 13.709/2018 (LGPD)",
    }
