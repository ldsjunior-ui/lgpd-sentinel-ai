# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Billing endpoints — Stripe checkout, webhooks, plan status, and API key management.
"""

import logging
from typing import Any, Optional

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.core.config import Settings, get_settings
from src.core.notifications import notify_new_subscriber, notify_cancellation
from src.core.database import (
    create_api_key,
    get_api_key,
    is_trial_active,
    update_api_key_plan,
)
from src.core.quota import get_usage, ANONYMOUS_KEY

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["Billing / Planos"])

# ─── Schemas ──────────────────────────────────────────────────────────────────


class GenerateKeyRequest(BaseModel):
    email: Optional[str] = Field(default=None, description="E-mail do usuário (opcional)")


class GenerateKeyResponse(BaseModel):
    api_key: str
    plan: str
    message: str


class CheckoutRequest(BaseModel):
    api_key: str = Field(..., description="API key existente para associar ao plano Pro")


class PlanStatusResponse(BaseModel):
    plan: str
    daily_limit: int
    requests_today: int
    requests_remaining: int
    trial_active: bool = False


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _get_limits(plan: str, settings: Settings) -> dict[str, Any]:
    if plan == "pro":
        return {"mappings": "unlimited", "dpias": "unlimited", "dsrs": "unlimited"}
    return {
        "mappings": settings.FREE_QUOTA_MAPPINGS,
        "dpias": settings.FREE_QUOTA_DPIAS,
        "dsrs": settings.FREE_QUOTA_DSRS,
    }


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.post("/keys", response_model=GenerateKeyResponse, summary="Gerar nova API key (free tier)")
async def generate_key(
    body: GenerateKeyRequest,
    settings: Settings = Depends(get_settings),
) -> GenerateKeyResponse:
    """
    Creates a new free-tier API key.
    Pass the key in the X-API-Key header on subsequent requests.
    """
    key = create_api_key(email=body.email)
    return GenerateKeyResponse(
        api_key=key,
        plan="trial",
        message=(
            "Trial Pro de 7 dias ativado! Uso ilimitado por 7 dias. "
            f"Após o trial: {settings.FREE_QUOTA_MAPPINGS} mapeamentos, "
            f"{settings.FREE_QUOTA_DPIAS} DPIAs e {settings.FREE_QUOTA_DSRS} DSRs/mês (free) "
            "ou upgrade para Pro ilimitado."
        ),
    )


@router.get("/status", response_model=PlanStatusResponse, summary="Status do plano atual")
async def plan_status(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> PlanStatusResponse:
    """Return current daily usage. Works without API key (free tier)."""
    api_key = x_api_key or ANONYMOUS_KEY

    # Determine plan
    plan = "free"
    trial_active = False
    if api_key != ANONYMOUS_KEY:
        key_info = get_api_key(api_key)
        if key_info:
            plan = key_info.get("plan", "free")
            if plan == "free" and is_trial_active(api_key):
                plan = "trial"
                trial_active = True

    # Get daily usage
    usage = get_usage(api_key)
    total_today = usage.get("total", 0)
    daily_limit = settings.FREE_QUOTA_DAILY if plan == "free" else 999
    remaining = max(0, daily_limit - total_today)

    return PlanStatusResponse(
        plan="GRATUITO" if plan == "free" else "PRO" if plan == "pro" else "TRIAL",
        daily_limit=daily_limit,
        requests_today=total_today,
        requests_remaining=remaining,
        trial_active=trial_active,
    )


@router.post("/checkout", summary="Criar sessão de checkout Stripe (upgrade para Pro)")
async def create_checkout(
    body: CheckoutRequest,
    settings: Settings = Depends(get_settings),
) -> dict:
    """
    Creates a Stripe Checkout Session for upgrading to Pro.
    Returns the checkout URL to redirect the user.
    """
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe não configurado. Defina STRIPE_SECRET_KEY no .env.",
        )
    if not settings.STRIPE_PRICE_ID_PRO:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="STRIPE_PRICE_ID_PRO não configurado no .env.",
        )

    key_info = get_api_key(body.api_key)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key não encontrada.",
        )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": settings.STRIPE_PRICE_ID_PRO, "quantity": 1}],
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={"api_key": body.api_key},
            customer_email=key_info.get("email") or None,
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except stripe.StripeError as e:
        logger.error("Stripe error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao criar sessão Stripe: {e.user_message}",
        )


@router.post("/webhook", summary="Webhook Stripe (uso interno)")
async def stripe_webhook(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """
    Handles Stripe webhook events:
    - checkout.session.completed → upgrade to Pro
    - customer.subscription.deleted → downgrade to free
    """
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        api_key = session.get("metadata", {}).get("api_key")
        if api_key:
            update_api_key_plan(
                api_key=api_key,
                plan="pro",
                stripe_customer_id=session.get("customer"),
                stripe_subscription_id=session.get("subscription"),
            )
            logger.info("Upgraded API key %s to Pro", api_key[:12] + "...")
            # Enviar notificação de email ao dono do produto
            notify_new_subscriber(
                customer_email=session.get("customer_email"),
                api_key=api_key,
                plan="pro",
                stripe_customer_id=session.get("customer"),
                stripe_subscription_id=session.get("subscription"),
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER or "",
                smtp_password=settings.SMTP_PASSWORD or "",
                notification_email=settings.NOTIFICATION_EMAIL,
                from_email=settings.SMTP_FROM,
            )

    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        if customer_id:
            # Find key by customer ID and downgrade
            from src.core.database import get_conn
            downgraded_key = None
            with get_conn() as conn:
                row = conn.execute(
                    "SELECT api_key FROM api_keys WHERE stripe_customer_id = ?", (customer_id,)
                ).fetchone()
                if row:
                    downgraded_key = row["api_key"]
                    update_api_key_plan(api_key=downgraded_key, plan="free")
                    logger.info("Downgraded customer %s to free", customer_id)
            # Enviar notificação de cancelamento
            notify_cancellation(
                stripe_customer_id=customer_id,
                api_key=downgraded_key,
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER or "",
                smtp_password=settings.SMTP_PASSWORD or "",
                notification_email=settings.NOTIFICATION_EMAIL,
                from_email=settings.SMTP_FROM,
            )

    return JSONResponse(content={"received": True})
