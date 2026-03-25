# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Unit tests for Data Mapping endpoint (src/api/routes/mapping.py).
Uses pytest + httpx AsyncClient for async FastAPI testing.
No external services needed - LLM calls are mocked.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.models.schemas import LGPDCategory, RiskLevel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_mapping_payload():
    """Valid data mapping request payload."""
    return {
        "data": [
            {"key": "cpf", "value": "123.456.789-00"},
            {"key": "nome_completo", "value": "Joao Silva"},
            {"key": "diagnostico_medico", "value": "Hipertensao"},
        ],
        "context": "Startup de telemedicina brasileira",
    }


@pytest.fixture
def mock_ollama_response():
    """Mock LLM response that returns valid LGPD mapping JSON."""
    return """
    {
        "mapeamento": [
            {
                "campo": "cpf",
                "categoria_lgpd": "dado_comum",
                "base_legal": "execucao_contrato",
                "artigo_lgpd": "Art. 7, inciso V",
                "nivel_risco": "alto",
                "requer_consentimento_explicito": false,
                "periodo_retencao": "5 anos apos encerramento da relacao",
                "medidas_seguranca": ["criptografia", "controle_de_acesso"],
                "observacoes": "CPF e dado de identificacao unica"
            },
            {
                "campo": "nome_completo",
                "categoria_lgpd": "dado_comum",
                "base_legal": "execucao_contrato",
                "artigo_lgpd": "Art. 7, inciso V",
                "nivel_risco": "baixo",
                "requer_consentimento_explicito": false,
                "periodo_retencao": "5 anos",
                "medidas_seguranca": ["controle_de_acesso"],
                "observacoes": "Dado de identificacao basica"
            },
            {
                "campo": "diagnostico_medico",
                "categoria_lgpd": "dado_sensivel",
                "base_legal": "consentimento",
                "artigo_lgpd": "Art. 11, inciso I",
                "nivel_risco": "critico",
                "requer_consentimento_explicito": true,
                "periodo_retencao": "20 anos conforme CFM",
                "medidas_seguranca": ["criptografia_ponta_a_ponta", "acesso_restrito_medicos"],
                "observacoes": "Dado de saude - categoria sensivel Art. 5, II"
            }
        ],
        "resumo": {
            "total_campos": 3,
            "campos_sensiveis": 1,
            "risco_geral": "alto",
            "score_conformidade": 65,
            "recomendacoes_principais": [
                "Implementar criptografia AES-256 para dados de saude",
                "Obter consentimento explicito para diagnosticos medicos"
            ]
        }
    }
    """


# ---------------------------------------------------------------------------
# Tests: POST /api/v1/map-data
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_map_data_success(sample_mapping_payload, mock_ollama_response):
    """Test successful data mapping with mocked LLM."""
    with patch(
        "src.api.routes.mapping.Ollama",
        return_value=AsyncMock(ainvoke=AsyncMock(return_value=mock_ollama_response)),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/map-data",
                json=sample_mapping_payload,
            )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "mapped_data" in data
    assert "compliance_score" in data
    assert "recommendations" in data
    assert "total_personal_data" in data
    assert "total_sensitive_data" in data
    assert len(data["mapped_data"]) == 3


@pytest.mark.asyncio
async def test_map_data_identifies_sensitive_data(sample_mapping_payload, mock_ollama_response):
    """Test that sensitive data (health records) is correctly identified."""
    with patch(
        "src.api.routes.mapping.Ollama",
        return_value=AsyncMock(ainvoke=AsyncMock(return_value=mock_ollama_response)),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/map-data",
                json=sample_mapping_payload,
            )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    health_field = next(
        (f for f in data["mapped_data"] if f["key"] == "diagnostico_medico"),
        None,
    )
    assert health_field is not None
    assert health_field["sensitive"] is True
    assert health_field["lgpd_category"] == LGPDCategory.SENSITIVE.value


@pytest.mark.asyncio
async def test_map_data_empty_payload():
    """Test that empty data returns 422 validation error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/map-data",
            json={"data": [], "context": "test"},
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_map_data_ollama_unavailable(sample_mapping_payload):
    """Test graceful error when Ollama is not available."""
    with patch(
        "src.api.routes.mapping.Ollama",
        return_value=AsyncMock(
            ainvoke=AsyncMock(side_effect=ConnectionError("Ollama not running"))
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/map-data",
                json=sample_mapping_payload,
            )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_map_data_fallback_classifier(sample_mapping_payload):
    """Test regex fallback classifier when LLM returns invalid JSON."""
    with patch(
        "src.api.routes.mapping.Ollama",
        return_value=AsyncMock(
            ainvoke=AsyncMock(return_value="I cannot process this request properly")
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/map-data",
                json=sample_mapping_payload,
            )

    # Should fall back to regex classifier and return 200
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 0 <= data["compliance_score"] <= 100


# ---------------------------------------------------------------------------
# Tests: Health Check
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check():
    """Test that the health check endpoint returns 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


# ---------------------------------------------------------------------------
# Tests: Schema validation
# ---------------------------------------------------------------------------


def test_risk_level_enum():
    """Test RiskLevel enum values."""
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MEDIUM.value == "medium"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.CRITICAL.value == "critical"


def test_lgpd_category_enum():
    """Test LGPDCategory enum values."""
    assert LGPDCategory.COMMON.value == "dado_comum"
    assert LGPDCategory.SENSITIVE.value == "dado_sensivel"
    assert LGPDCategory.CHILD.value == "dado_crianca_adolescente"
    assert LGPDCategory.ANONYMOUS.value == "dado_anonimo"
