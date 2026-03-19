# LGPD Sentinel AI - Test Configuration
# Apache 2.0 License

"""pytest configuration and shared fixtures for LGPD Sentinel AI tests."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from src.main import app


@pytest.fixture(autouse=True)
def bypass_quota():
    """Disable quota enforcement in all unit tests to avoid DB state pollution."""
    with (
        patch("src.core.quota.get_usage", return_value={"mappings": 0, "dpias": 0, "dsrs": 0}),
        patch("src.core.quota.increment_usage", return_value=None),
    ):
        yield


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for async tests."""
    return "asyncio"


@pytest.fixture
async def client():
    """Async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_data_items():
    """Sample data items for testing data mapping."""
    return [
        {"key": "email", "value": "usuario@exemplo.com.br"},
        {"key": "cpf", "value": "123.456.789-00"},
    ]


@pytest.fixture
def sample_dpia_request():
    """Sample DPIA/RIPD request for testing."""
    return {
        "company_name": "Empresa Teste LTDA",
        "treatment_description": "Coleta de dados de clientes para CRM",
        "data_types": ["nome", "email", "cpf", "telefone"],
        "purposes": ["gestao_de_clientes", "marketing"],
        "industry_sector": "tecnologia",
    }
