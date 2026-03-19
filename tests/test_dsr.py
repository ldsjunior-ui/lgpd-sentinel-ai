# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Unit tests for DSR endpoint (src/api/routes/dsr.py).
LLM calls are mocked — no Ollama required.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from src.main import app


MOCK_DSR_JSON = """
{
    "pode_atender": true,
    "artigo_lgpd": "Art. 18, inciso II",
    "justificativa": "Empresa tem obrigação de fornecer acesso aos dados tratados.",
    "prazo_resposta_dias": 15,
    "requer_dpo": false,
    "requer_anpd": false,
    "acoes_requeridas": [
        {
            "acao": "Compilar relatório de dados do titular",
            "responsavel": "DPO / Equipe de TI",
            "prazo": "10 dias úteis"
        }
    ],
    "resposta_ao_titular": "Prezado titular, confirmamos o recebimento da sua solicitação...",
    "documentacao_necessaria": [
        "Documento de identidade do titular",
        "Registro da solicitação no sistema"
    ]
}
"""


@pytest.fixture
def dsr_payload():
    return {
        "company_name": "TechBrasil LTDA",
        "request_type": "acesso",
        "request_description": "Solicito acesso a todos os meus dados pessoais armazenados.",
        "data_context": "CRM de clientes",
        "titular_name": "João Silva",
    }


# ---------------------------------------------------------------------------
# POST /api/v1/dsr/analyze
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dsr_analyze_success(dsr_payload):
    with patch(
        "src.api.routes.dsr.Ollama",
        return_value=AsyncMock(ainvoke=AsyncMock(return_value=MOCK_DSR_JSON)),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/dsr/analyze", json=dsr_payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "pode_atender" in data
    assert "artigo_lgpd" in data
    assert "prazo_resposta_dias" in data
    assert "acoes_requeridas" in data
    assert "resposta_ao_titular" in data


@pytest.mark.asyncio
async def test_dsr_analyze_all_request_types(dsr_payload):
    """All 8 DSR types defined in Art. 18 should be accepted."""
    types = [
        "acesso", "correcao", "exclusao", "portabilidade",
        "oposicao", "revogacao_consentimento", "restricao", "informacao",
    ]
    for req_type in types:
        payload = {**dsr_payload, "request_type": req_type}
        with patch(
            "src.api.routes.dsr.Ollama",
            return_value=AsyncMock(ainvoke=AsyncMock(return_value=MOCK_DSR_JSON)),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/api/v1/dsr/analyze", json=payload)

        assert response.status_code == status.HTTP_200_OK, f"Failed for type: {req_type}"


@pytest.mark.asyncio
async def test_dsr_analyze_short_description_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/dsr/analyze",
            json={
                "request_type": "acesso",
                "request_description": "curto",  # < 10 chars
            },
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_dsr_analyze_invalid_request_type(dsr_payload):
    payload = {**dsr_payload, "request_type": "tipo_inexistente"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/dsr/analyze", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_dsr_analyze_ollama_unavailable(dsr_payload):
    with patch(
        "src.api.routes.dsr.Ollama",
        return_value=AsyncMock(
            ainvoke=AsyncMock(side_effect=ConnectionError("Ollama not running"))
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/dsr/analyze", json=dsr_payload)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_dsr_analyze_optional_fields_omitted():
    """company_name, data_context and titular_name are all optional."""
    with patch(
        "src.api.routes.dsr.Ollama",
        return_value=AsyncMock(ainvoke=AsyncMock(return_value=MOCK_DSR_JSON)),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/dsr/analyze",
                json={
                    "request_type": "exclusao",
                    "request_description": "Quero que todos os meus dados sejam eliminados.",
                },
            )

    assert response.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# GET /api/v1/dsr/types
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dsr_types_returns_all_eight():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/dsr/types")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "direitos" in data
    assert len(data["direitos"]) == 8
