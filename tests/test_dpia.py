# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Unit tests for DPIA endpoint (src/api/routes/dpia.py).
LLM calls are mocked — no Ollama required.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from src.main import app


MOCK_DPIA_JSON = """
{
    "nivel_risco": "alto",
    "score_conformidade": 72,
    "base_legal": "consentimento",
    "dpo_necessario": true,
    "notificar_anpd": false,
    "riscos_identificados": [
        "Dados sensíveis de saúde sem criptografia end-to-end",
        "Compartilhamento com terceiros sem cláusula LGPD"
    ],
    "medidas_mitigacao": [
        {"medida": "Implementar criptografia AES-256 em repouso", "prioridade": "alta"},
        {"medida": "Revisar contratos com processadores de dados", "prioridade": "media"}
    ],
    "recomendacoes": [
        "Nomear DPO interno ou terceirizado",
        "Documentar base legal para cada tratamento"
    ]
}
"""


@pytest.fixture
def dpia_payload():
    return {
        "company_name": "Clínica Saúde Total LTDA",
        "treatment_description": "Armazenamento de prontuários médicos eletrônicos",
        "data_types": ["nome", "cpf", "diagnostico", "historico_medico"],
        "purposes": ["atendimento_medico", "faturamento_convenios"],
        "industry_sector": "saude",
    }


# ---------------------------------------------------------------------------
# POST /api/v1/dpia/generate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dpia_generate_success(dpia_payload):
    with patch(
        "src.api.routes.dpia.Ollama",
        return_value=AsyncMock(ainvoke=AsyncMock(return_value=MOCK_DPIA_JSON)),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/dpia/generate", json=dpia_payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "risk_level" in data
    assert "compliance_score" in data
    assert "risks" in data
    assert "mitigation_measures" in data


@pytest.mark.asyncio
async def test_dpia_generate_returns_risk_level(dpia_payload):
    with patch(
        "src.api.routes.dpia.Ollama",
        return_value=AsyncMock(ainvoke=AsyncMock(return_value=MOCK_DPIA_JSON)),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/dpia/generate", json=dpia_payload)

    data = response.json()
    assert data["risk_level"] in ("low", "medium", "high", "critical")


@pytest.mark.asyncio
async def test_dpia_generate_missing_required_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/dpia/generate",
            json={"company_name": "Empresa X"},  # missing required fields
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_dpia_generate_ollama_unavailable(dpia_payload):
    with patch(
        "src.api.routes.dpia.Ollama",
        return_value=AsyncMock(
            ainvoke=AsyncMock(side_effect=ConnectionError("Ollama not running"))
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/dpia/generate", json=dpia_payload)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_dpia_generate_llm_invalid_json(dpia_payload):
    """Fallback should handle unparseable LLM output gracefully."""
    with patch(
        "src.api.routes.dpia.Ollama",
        return_value=AsyncMock(
            ainvoke=AsyncMock(return_value="Desculpe, não consegui processar.")
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/dpia/generate", json=dpia_payload)

    # Should not crash — either 200 with fallback or 500 with clear error
    assert response.status_code in (
        status.HTTP_200_OK,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# ---------------------------------------------------------------------------
# POST /api/v1/dpia/generate/pdf
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dpia_pdf_returns_bytes(dpia_payload):
    with patch(
        "src.api.routes.dpia.Ollama",
        return_value=AsyncMock(ainvoke=AsyncMock(return_value=MOCK_DPIA_JSON)),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/dpia/generate/pdf", json=dpia_payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 100  # non-empty PDF
