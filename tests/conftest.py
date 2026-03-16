# LGPD Sentinel AI - Test Configuration
# Apache 2.0 License

"""pytest configuration and shared fixtures for LGPD Sentinel AI tests."""

import pytest
from httpx import AsyncClient

from src.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for async tests."""
    return "asyncio"


@pytest.fixture
async def client():
    """Async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_data_items():
    """Sample data items for testing data mapping."""
    return [
        {
            "field_name": "email",
            "field_type": "string",
            "description": "Email do usuario",
            "sample_value": "usuario@exemplo.com.br",
        },
        {
            "field_name": "cpf",
            "field_type": "string",
            "description": "CPF do cliente",
            "sample_value": "123.456.789-00",
        },
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
