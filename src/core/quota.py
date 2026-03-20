# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Quota enforcement for freemium plans.
Usage: inject `QuotaCheck("mappings")` as a FastAPI dependency.
"""

from fastapi import Depends, Header, HTTPException, status

from src.core.config import get_settings, Settings
from src.core.database import get_api_key, get_usage, increment_usage, is_trial_active

# Sentinel key used when no X-API-Key header is provided (anonymous / demo)
ANONYMOUS_KEY = "__anonymous__"

# Per-plan monthly limits (None = unlimited)
PLAN_LIMITS: dict[str, dict[str, int | None]] = {
    "free": {"mappings": None, "dpias": None, "dsrs": None},  # set from settings
    "pro":  {"mappings": None, "dpias": None, "dsrs": None},  # unlimited
}


def _get_limits(plan: str, settings: Settings) -> dict[str, int | None]:
    if plan in ("pro", "trial"):
        return {"mappings": None, "dpias": None, "dsrs": None}
    return {
        "mappings": settings.FREE_QUOTA_MAPPINGS,
        "dpias": settings.FREE_QUOTA_DPIAS,
        "dsrs": settings.FREE_QUOTA_DSRS,
    }


class QuotaCheck:
    """FastAPI dependency factory. Usage: Depends(QuotaCheck('mappings'))"""

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def __call__(
        self,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
        settings: Settings = Depends(get_settings),
    ) -> dict:
        """
        Validate API key, check quota, and return key info dict.
        If no key is provided, treat as anonymous free-tier user.
        """
        api_key = x_api_key or ANONYMOUS_KEY

        # Look up key in DB (anonymous key is always free)
        if api_key == ANONYMOUS_KEY:
            key_info = {"api_key": ANONYMOUS_KEY, "plan": "free", "email": None}
        else:
            key_info = get_api_key(api_key)
            if not key_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or inactive API key.",
                )

        plan = key_info.get("plan", "free")
        # Treat as Pro during active trial period
        if plan == "free" and api_key != ANONYMOUS_KEY and is_trial_active(api_key):
            plan = "trial"
        limits = _get_limits(plan, settings)
        limit = limits.get(self.endpoint)

        if limit is not None:
            usage = get_usage(api_key)
            used = usage.get(self.endpoint, 0)
            if used >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Monthly quota exceeded for '{self.endpoint}' "
                        f"({used}/{limit}). Upgrade to Pro for unlimited access."
                    ),
                )

        # Increment usage after passing the check
        increment_usage(api_key, self.endpoint)

        return key_info
