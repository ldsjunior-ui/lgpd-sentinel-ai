# Copyright 2024 LGPD Sentinel AI Contributors
#
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

"""Configuration management for LGPD Sentinel AI."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App metadata
    APP_NAME: str = "LGPD Sentinel AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")

    # API settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = Field(default=["*"])

    # Ollama / LLM settings (local inference, zero-cost)
    OLLAMA_BASE_URL: str = Field(default="http://ollama:11434")
    OLLAMA_MODEL: str = Field(default="mistral")
    LLM_TEMPERATURE: float = Field(default=0.1, ge=0.0, le=2.0)
    LLM_MAX_TOKENS: int = Field(default=4096)

    # Supabase settings (free tier, optional)
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None)
    SUPABASE_SERVICE_KEY: Optional[str] = Field(default=None)

    # Report / PDF settings
    REPORTS_DIR: str = Field(default="/tmp/lgpd_reports")
    REPORT_COMPANY_NAME: str = Field(default="Empresa")

    # LGPD compliance risk thresholds
    RISK_HIGH_THRESHOLD: float = Field(default=0.7, ge=0.0, le=1.0)
    RISK_MEDIUM_THRESHOLD: float = Field(default=0.4, ge=0.0, le=1.0)


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance. Use as FastAPI dependency."""
    return Settings()


# Convenience singleton for direct imports
settings = get_settings()
