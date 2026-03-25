# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Quota enforcement — free tier with daily limits.
8 analyses per day (mapping + DPIA + DSR combined), no API key required.
"""

import logging
from datetime import date

from fastapi import Depends, Header, HTTPException, status

from src.core.config import get_settings, Settings
from src.core.database import get_api_key, is_trial_active

logger = logging.getLogger(__name__)

# In-memory daily usage counter (resets each day)
_daily_usage: dict[str, dict[str, int]] = {}
_usage_date: date | None = None


def _reset_if_new_day() -> None:
    """Reset counters at midnight."""
    global _daily_usage, _usage_date
    today = date.today()
    if _usage_date != today:
        _daily_usage = {}
        _usage_date = today


def get_usage(api_key: str) -> dict[str, int]:
    """Get current daily usage for a key."""
    _reset_if_new_day()
    return _daily_usage.get(api_key, {"mappings": 0, "dpias": 0, "dsrs": 0, "total": 0})


def increment_usage(api_key: str, endpoint: str) -> None:
    """Increment daily usage counter."""
    _reset_if_new_day()
    if api_key not in _daily_usage:
        _daily_usage[api_key] = {"mappings": 0, "dpias": 0, "dsrs": 0, "total": 0}
    _daily_usage[api_key][endpoint] = _daily_usage[api_key].get(endpoint, 0) + 1
    _daily_usage[api_key]["total"] = _daily_usage[api_key].get("total", 0) + 1


# Sentinel key for anonymous users
ANONYMOUS_KEY = "__anonymous__"


class QuotaCheck:
    """FastAPI dependency. Free: 8/day total. Pro/Trial: unlimited."""

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def __call__(
        self,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
        settings: Settings = Depends(get_settings),
    ) -> dict:
        api_key = x_api_key or ANONYMOUS_KEY

        # Look up key (anonymous = free, always valid)
        if api_key == ANONYMOUS_KEY:
            key_info = {"api_key": ANONYMOUS_KEY, "plan": "free", "email": None}
        else:
            key_info = get_api_key(api_key)
            if not key_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Chave API inválida ou inativa.",
                )

        plan = key_info.get("plan", "free")

        # Trial = unlimited
        if plan == "free" and api_key != ANONYMOUS_KEY and is_trial_active(api_key):
            plan = "trial"

        # Pro/Trial = unlimited
        if plan in ("pro", "trial"):
            increment_usage(api_key, self.endpoint)
            return key_info

        # Free tier: 8 analyses per day (total across all endpoints)
        daily_limit = settings.FREE_QUOTA_DAILY
        usage = get_usage(api_key)
        total_used = usage.get("total", 0)

        if total_used >= daily_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Limite diário atingido ({total_used}/{daily_limit} análises hoje). "
                    f"Volte amanhã ou gere uma API Key para trial Pro ilimitado de 7 dias."
                ),
            )

        increment_usage(api_key, self.endpoint)
        return key_info
