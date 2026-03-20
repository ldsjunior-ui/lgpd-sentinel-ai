# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Integration tests — require Ollama running with llama3.1:8b.

Run with:
    pytest tests/test_integration.py -m integration -v --timeout=300

Skipped automatically in CI unless LGPD_RUN_INTEGRATION=1 is set.
"""

import os

import pytest
import httpx

# Skip entire module unless explicitly opted in
pytestmark = pytest.mark.skipif(
    os.getenv("LGPD_RUN_INTEGRATION") != "1",
    reason="Integration tests require Ollama. Set LGPD_RUN_INTEGRATION=1 to run.",
)

API_BASE = "http://localhost:8000/api/v1"
TIMEOUT = 600  # Ollama cold-start (model load from disk) can take ~120s on slower machines


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def ollama_is_available() -> bool:
    try:
        r = httpx.get("http://localhost:11434/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def api_is_available() -> bool:
    try:
        r = httpx.get("http://localhost:8000/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Integration: Data Mapping (real LLM)
# ---------------------------------------------------------------------------


def test_integration_mapping_with_real_ollama():
    """POST /api/v1/map-data — uses real llama3.1:8b inference."""
    assert ollama_is_available(), "Ollama is not running at localhost:11434"
    assert api_is_available(), "API is not running at localhost:8000"

    payload = {
        "data": [
            {"key": "cpf", "value": "123.456.789-00"},
            {"key": "email", "value": "usuario@exemplo.com.br"},
            {"key": "diagnostico_medico", "value": "Diabetes tipo 2"},
        ],
        "context": "Sistema de gestão de pacientes de clínica médica",
    }

    response = httpx.post(f"{API_BASE}/map-data", json=payload, timeout=TIMEOUT)

    assert response.status_code == 200
    data = response.json()

    assert "mapped_data" in data
    assert "compliance_score" in data
    assert isinstance(data["compliance_score"], (int, float))
    assert 0 <= data["compliance_score"] <= 100
    assert len(data["mapped_data"]) == 3

    # Health data should be identified as sensitive
    sensitive_fields = [f for f in data["mapped_data"] if f.get("sensitive")]
    assert len(sensitive_fields) >= 1, "At least one field should be flagged as sensitive"


# ---------------------------------------------------------------------------
# Integration: DPIA (real LLM)
# ---------------------------------------------------------------------------


def test_integration_dpia_generate_with_real_ollama():
    """POST /api/v1/dpia/generate — uses real llama3.1:8b inference."""
    assert ollama_is_available(), "Ollama is not running"
    assert api_is_available(), "API is not running"

    payload = {
        "company_name": "Fintech Crédito SA",
        "treatment_description": "Análise de crédito com dados financeiros e score de risco",
        "data_types": ["cpf", "renda_mensal", "historico_pagamentos", "score_serasa"],
        "purposes": ["concessao_credito", "prevencao_fraudes"],
        "industry_sector": "financeiro",
    }

    response = httpx.post(f"{API_BASE}/dpia/generate", json=payload, timeout=TIMEOUT)

    assert response.status_code == 200
    data = response.json()

    assert "risk_level" in data
    assert data["risk_level"] in ("low", "medium", "high", "critical")
    assert "compliance_score" in data
    assert "risks" in data
    assert isinstance(data["risks"], list)
    assert len(data["risks"]) > 0


def test_integration_dpia_pdf_with_real_ollama():
    """POST /api/v1/dpia/generate/pdf — generates a real PDF."""
    assert ollama_is_available(), "Ollama is not running"
    assert api_is_available(), "API is not running"

    payload = {
        "company_name": "E-commerce Brasil LTDA",
        "treatment_description": "Gestão de pedidos e entrega de produtos",
        "data_types": ["nome", "cpf", "endereco", "dados_cartao_tokenizado"],
        "purposes": ["processamento_pedidos", "entrega"],
    }

    response = httpx.post(f"{API_BASE}/dpia/generate/pdf", json=payload, timeout=TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 500  # meaningful PDF


# ---------------------------------------------------------------------------
# Integration: DSR (real LLM)
# ---------------------------------------------------------------------------


def test_integration_dsr_analyze_with_real_ollama():
    """POST /api/v1/dsr/analyze — uses real llama3.1:8b inference."""
    assert ollama_is_available(), "Ollama is not running"
    assert api_is_available(), "API is not running"

    payload = {
        "company_name": "Marketplace Digital SA",
        "request_type": "exclusao",
        "request_description": (
            "Solicito a eliminação de todos os meus dados pessoais "
            "armazenados pela empresa, incluindo histórico de compras e dados cadastrais."
        ),
        "data_context": "Plataforma de e-commerce, base MySQL de clientes",
        "titular_name": "Maria Santos",
    }

    response = httpx.post(f"{API_BASE}/dsr/analyze", json=payload, timeout=TIMEOUT)

    assert response.status_code == 200
    data = response.json()

    assert "pode_atender" in data
    assert isinstance(data["pode_atender"], bool)
    assert "prazo_resposta_dias" in data
    assert data["prazo_resposta_dias"] <= 15  # LGPD Art. 18 §5 limit
    assert "resposta_ao_titular" in data
    assert len(data["resposta_ao_titular"]) > 20  # non-trivial response


# ---------------------------------------------------------------------------
# Integration: Health + end-to-end smoke test
# ---------------------------------------------------------------------------


def test_integration_health_check():
    """Verify the full stack is healthy before integration tests."""
    assert api_is_available(), "API is not running at localhost:8000"

    response = httpx.get("http://localhost:8000/health", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
