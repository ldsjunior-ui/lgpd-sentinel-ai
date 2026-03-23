# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""Pydantic models and enums for LGPD Sentinel AI."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class LGPDCategory(str, Enum):
    """LGPD data classification categories."""

    COMMON = "dado_comum"
    SENSITIVE = "dado_sensivel"
    CHILD = "dado_crianca_adolescente"
    ANONYMOUS = "dado_anonimo"
    NAO_CLASSIFICADO = "nao_classificado"


class RiskLevel(str, Enum):
    """Risk level classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Data Mapping
# ---------------------------------------------------------------------------


class DataItem(BaseModel):
    """A single data field for LGPD classification."""

    key: str = Field(..., description="Nome do campo de dado")
    value: str = Field(..., description="Valor de exemplo do campo")
    sensitive: bool = Field(default=False, description="Se o dado e sensivel conforme LGPD")
    lgpd_category: LGPDCategory = Field(
        default=LGPDCategory.NAO_CLASSIFICADO,
        description="Categoria LGPD do dado",
    )
    legal_basis: Optional[str] = Field(
        default=None, description="Base legal conforme LGPD Art. 7 ou 11"
    )
    artigo_lgpd: Optional[str] = Field(
        default=None, description="Artigo da LGPD aplicavel (ex: Art. 7, V ou Art. 11, I)"
    )


class DataMappingRequest(BaseModel):
    """Request body for the data mapping endpoint."""

    data: list[DataItem] = Field(
        ..., min_length=1, description="Lista de dados para classificacao LGPD"
    )
    context: Optional[str] = Field(
        default=None, description="Contexto do tratamento de dados"
    )


class DataMappingResponse(BaseModel):
    """Response from the data mapping endpoint."""

    mapped_data: list[DataItem] = Field(description="Dados classificados conforme LGPD")
    compliance_score: float = Field(
        ge=0, le=100, description="Score de conformidade LGPD (0-100)"
    )
    recommendations: list[str] = Field(description="Recomendacoes de conformidade")
    total_personal_data: int = Field(description="Total de dados pessoais identificados")
    total_sensitive_data: int = Field(description="Total de dados sensiveis identificados")


# ---------------------------------------------------------------------------
# DPIA / RIPD
# ---------------------------------------------------------------------------


class DPIARequest(BaseModel):
    """Request body for DPIA/RIPD generation."""

    company_name: Optional[str] = Field(default=None, description="Nome da empresa")
    treatment_description: str = Field(
        ..., min_length=10, description="Descricao do tratamento de dados"
    )
    data_types: list[str] = Field(
        default_factory=list, description="Tipos de dados tratados"
    )
    purposes: list[str] = Field(
        default_factory=list, description="Finalidades do tratamento"
    )
    industry_sector: Optional[str] = Field(
        default=None, description="Setor de atuacao da empresa"
    )


class DPIAResponse(BaseModel):
    """Response from DPIA/RIPD generation."""

    model_config = {"protected_namespaces": ()}

    company_name: str
    treatment_description: str
    legal_basis: str
    applicable_articles: list[str] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)
    mitigation_measures: list[dict[str, Any]] = Field(default_factory=list)
    overall_risk_score: float = Field(ge=0, le=1)
    risk_level: RiskLevel
    compliance_score: float = Field(ge=0, le=100)
    recommendations: list[str] = Field(default_factory=list)
    requires_anpd_consultation: bool = False
    anpd_consultation_reason: Optional[str] = None
    generated_at: datetime
    model_used: str
    raw_llm_output: Optional[str] = None


# ---------------------------------------------------------------------------
# Common
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str


__all__ = [
    "DataItem",
    "DataMappingRequest",
    "DataMappingResponse",
    "DPIARequest",
    "DPIAResponse",
    "ErrorResponse",
    "LGPDCategory",
    "RiskLevel",
]
