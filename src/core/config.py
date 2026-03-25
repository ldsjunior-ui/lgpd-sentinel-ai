# Copyright 2024 LGPD Sentinel AI Contributors
#
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

"""Configuration management for LGPD Sentinel AI."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> str:
    """Return platform-appropriate app data directory."""
    env = os.environ.get("LGPD_DATA_DIR")
    if env:
        return env
    if os.name == "nt":  # Windows
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return str(Path(base) / "LGPD Sentinel AI")
    elif os.uname().sysname == "Darwin":  # macOS
        return str(Path.home() / "Library" / "Application Support" / "LGPD Sentinel AI")
    else:  # Linux
        xdg = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
        return str(Path(xdg) / "lgpd-sentinel-ai")


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
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")

    # API settings
    API_V1_PREFIX: str = "/api/v1"
    # Production: only localhost. Use CORS_ORIGINS env var to override in dev.
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:*", "https://localhost:*", "tauri://localhost"])

    # Ollama / LLM settings (local inference, zero-cost)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="mistral")
    LLM_TEMPERATURE: float = Field(default=0.0, ge=0.0, le=2.0)
    LLM_MAX_TOKENS: int = Field(default=4096)

    # Supabase settings (free tier, optional)
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None)
    SUPABASE_SERVICE_KEY: Optional[str] = Field(default=None)

    # Data directory (platform-aware)
    DATA_DIR: str = Field(default_factory=_default_data_dir)
    DB_PATH: str = Field(default="")  # auto-set from DATA_DIR if empty

    # Report / PDF settings
    REPORTS_DIR: str = Field(default="")  # auto-set from DATA_DIR if empty
    REPORT_COMPANY_NAME: str = Field(default="Empresa")

    # LGPD compliance risk thresholds
    RISK_HIGH_THRESHOLD: float = Field(default=0.7, ge=0.0, le=1.0)
    RISK_MEDIUM_THRESHOLD: float = Field(default=0.4, ge=0.0, le=1.0)

    # ── FUTURE / OPTIONAL FEATURES ──────────────────────────────────────────
    # The settings below are NOT used in the default local-only mode.
    # They exist as preparation for future SaaS/cloud scenarios.
    # In local mode, NO external connections are made — all processing
    # happens on your machine via Ollama. No telemetry, no tracking.

    # Stripe (future: freemium monetization — NOT active in local mode)
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None)
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None)
    STRIPE_PRICE_ID_PRO: Optional[str] = Field(default=None)
    STRIPE_SUCCESS_URL: str = Field(default="http://localhost:8501?checkout=success")
    STRIPE_CANCEL_URL: str = Field(default="http://localhost:8501?checkout=cancel")

    # Local quota limits (enforced locally, no external calls)
    # Free plan: 8 total analyses per day (mapping + DPIA + DSR combined)
    FREE_QUOTA_DAILY: int = Field(default=8)
    FREE_QUOTA_MAPPINGS: int = Field(default=8)
    FREE_QUOTA_DPIAS: int = Field(default=8)
    FREE_QUOTA_DSRS: int = Field(default=8)

    # Email notifications (future: optional SMTP — NOT active by default)
    # Only used if user explicitly configures SMTP credentials.
    SMTP_HOST: str = Field(default="")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    SMTP_FROM: str = Field(default="")
    NOTIFICATION_EMAIL: str = Field(default="")


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance. Use as FastAPI dependency."""
    s = Settings()
    # Auto-set paths from DATA_DIR if not explicitly configured
    data_dir = Path(s.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    if not s.DB_PATH:
        s.DB_PATH = str(data_dir / "sentinel.db")
    if not s.REPORTS_DIR:
        s.REPORTS_DIR = str(data_dir / "reports")
    Path(s.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    return s


# Convenience singleton for direct imports
settings = get_settings()
