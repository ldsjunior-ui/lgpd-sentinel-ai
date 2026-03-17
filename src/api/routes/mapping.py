# LGPD Sentinel AI - Endpoint de Data Mapping
# Identifica dados pessoais usando LangChain + Ollama (gratuito e local)
# Apache 2.0

import json
import logging
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
import pandas as pd
from io import StringIO

from langchain_community.llms import Ollama

from src.core.config import Settings, get_settings
from src.core.prompts import DATA_MAPPING_TEMPLATE
from src.models.schemas import (
    DataMappingRequest,
    DataMappingResponse,
    DataItem,
    LGPDCategory,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from LLM output that may contain extra text."""
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

    return {}


@router.post(
    "/map-data",
    response_model=DataMappingResponse,
    summary="Mapear dados pessoais conforme LGPD",
    description=(
        "Analisa uma lista de dados e classifica cada item conforme a LGPD usando IA "
        "(Mistral via Ollama). Identifica dados pessoais (Art. 5, I), dados sensiveis "
        "(Art. 5, II), sugere bases legais e calcula score de conformidade."
    ),
)
async def map_data(
    request: DataMappingRequest,
    settings: Settings = Depends(get_settings),
):
    """Endpoint principal de data mapping LGPD."""
    data_items_str = "\n".join(
        f"- {item.key}: {item.value}" for item in request.data
    )
    context = request.context or "nao especificado"

    try:
        llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )
        prompt = DATA_MAPPING_TEMPLATE.format(
            data_items=data_items_str,
            company_context=context,
        )
        result = await llm.ainvoke(prompt)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama nao disponivel: {exc}. Execute: ollama pull {settings.OLLAMA_MODEL}",
        ) from exc

    # Parse LLM JSON output
    analysis = _extract_json(str(result))
    classificacoes = analysis.get("mapeamento", analysis.get("classificacoes", []))

    if not classificacoes:
        # Fallback: regex classification when LLM output is unparseable
        classificacoes = _classify_by_regex(request.data)
        compliance_score = 60.0
        recommendations = [
            "Execute o audit completo com Ollama para analise mais precisa",
            "Verifique se todos os dados tem base legal documentada",
        ]
    else:
        resumo = analysis.get("resumo", {})
        compliance_score = float(resumo.get("score_conformidade", 50))
        recommendations = resumo.get(
            "recomendacoes_principais",
            analysis.get("recommendations", []),
        )

    # Build response
    mapped_items = []
    for item in request.data:
        classificacao = next(
            (
                c
                for c in classificacoes
                if c.get("key") == item.key or c.get("campo") == item.key
            ),
            {
                "is_sensitive": False,
                "lgpd_category": "nao_classificado",
                "categoria_lgpd": "nao_classificado",
                "legal_basis": None,
            },
        )

        is_sensitive = classificacao.get("is_sensitive", False) or classificacao.get(
            "categoria_lgpd", ""
        ) == "dado_sensivel"

        category_value = classificacao.get(
            "lgpd_category",
            classificacao.get("categoria_lgpd", "nao_classificado"),
        )
        try:
            category = LGPDCategory(category_value)
        except ValueError:
            category = LGPDCategory.NAO_CLASSIFICADO

        mapped_items.append(
            DataItem(
                key=item.key,
                value=item.value,
                sensitive=is_sensitive,
                lgpd_category=category,
                legal_basis=classificacao.get(
                    "legal_basis", classificacao.get("base_legal")
                ),
            )
        )

    total_personal = sum(
        1 for i in mapped_items if i.lgpd_category != LGPDCategory.NAO_CLASSIFICADO
    )
    total_sensitive = sum(1 for i in mapped_items if i.sensitive)

    return DataMappingResponse(
        mapped_data=mapped_items,
        compliance_score=compliance_score,
        recommendations=recommendations,
        total_personal_data=total_personal,
        total_sensitive_data=total_sensitive,
    )


@router.post(
    "/map-data/upload",
    response_model=DataMappingResponse,
    summary="Mapear dados a partir de arquivo CSV/JSON",
    description="Faz upload de arquivo CSV ou JSON e analisa os dados conforme LGPD.",
)
async def map_data_from_file(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    """Aceita upload de arquivo CSV ou JSON e executa o data mapping LGPD."""
    if not file.filename or not file.filename.endswith((".csv", ".json")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato nao suportado. Use CSV ou JSON.",
        )

    content = await file.read()

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(StringIO(content.decode("utf-8")))
            data_items = [
                DataItem(key=col, value=str(df[col].iloc[0]))
                for col in df.columns
                if not df[col].empty
            ]
        else:
            data_dict = json.loads(content.decode("utf-8"))
            if isinstance(data_dict, list):
                data_dict = data_dict[0] if data_dict else {}
            data_items = [
                DataItem(key=k, value=str(v)) for k, v in data_dict.items()
            ]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar arquivo: {exc}",
        ) from exc

    request = DataMappingRequest(data=data_items)
    return await map_data(request, settings)


def _classify_by_regex(data: list[DataItem]) -> list[dict]:
    """Regex-based fallback classifier when Ollama is unavailable."""
    sensitive_patterns = {
        "cpf": r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",
        "rg": r"\d{1,2}\.?\d{3}\.?\d{3}-?[\dxX]",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "telefone": r"\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}",
        "data_nascimento": r"\d{2}/\d{2}/\d{4}",
    }

    sensitive_keys = [
        "saude", "health", "biometrico", "biometric", "racial",
        "religiao", "religion", "politico", "political", "sexual",
    ]

    result = []
    for item in data:
        is_sensitive = any(k in item.key.lower() for k in sensitive_keys)
        is_personal = any(
            re.search(p, item.value) for p in sensitive_patterns.values()
        )

        if is_sensitive:
            category = "dado_sensivel"
        elif is_personal:
            category = "dado_pessoal"
        else:
            category = "nao_classificado"

        result.append(
            {
                "key": item.key,
                "is_personal": is_personal or is_sensitive,
                "is_sensitive": is_sensitive,
                "lgpd_category": category,
                "legal_basis": "Verificar base legal conforme LGPD Art. 7",
            }
        )

    return result
