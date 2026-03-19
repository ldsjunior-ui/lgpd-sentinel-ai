# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Email notification system — zero external dependencies.
Uses Python's built-in smtplib + email modules.
Supports any SMTP server (Gmail, Outlook/Hotmail, Brevo, SendGrid, etc.)

Designed to never crash the caller — all errors are logged, never re-raised.
"""

import logging
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


def _build_new_subscriber_email(
    to_email: str,
    customer_email: Optional[str],
    api_key: str,
    plan: str,
    stripe_customer_id: Optional[str],
    stripe_subscription_id: Optional[str],
) -> MIMEMultipart:
    """Compose HTML email for new Pro subscriber."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎉 Novo assinante Pro — LGPD Sentinel AI"
    msg["To"] = to_email

    timestamp = datetime.utcnow().strftime("%d/%m/%Y às %H:%M UTC")

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
    .card {{ background: white; border-radius: 8px; padding: 30px; max-width: 600px;
             margin: 0 auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .badge {{ display: inline-block; background: #22c55e; color: white;
              padding: 4px 12px; border-radius: 20px; font-size: 13px; }}
    .label {{ color: #6b7280; font-size: 13px; margin-top: 16px; }}
    .value {{ color: #111827; font-size: 15px; font-weight: bold; margin-top: 2px; }}
    .footer {{ margin-top: 24px; font-size: 12px; color: #9ca3af; }}
    hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
  </style>
</head>
<body>
  <div class="card">
    <h2 style="color:#111827; margin-top:0;">🛡️ LGPD Sentinel AI</h2>
    <span class="badge">Novo assinante Pro ✓</span>
    <p style="color:#374151; margin-top:16px;">
      Um novo usuário acaba de assinar o plano <strong>Pro</strong>!
    </p>
    <hr>
    <div class="label">📅 Data/hora</div>
    <div class="value">{timestamp}</div>

    <div class="label">📧 Email do cliente</div>
    <div class="value">{customer_email or "Não informado"}</div>

    <div class="label">💳 Plano</div>
    <div class="value">{plan.upper()}</div>

    <div class="label">🔑 API Key</div>
    <div class="value" style="font-family:monospace;font-size:13px;">{api_key[:20]}...</div>

    <div class="label">🏷️ Stripe Customer ID</div>
    <div class="value" style="font-family:monospace;font-size:13px;">{stripe_customer_id or "N/A"}</div>

    <div class="label">📋 Subscription ID</div>
    <div class="value" style="font-family:monospace;font-size:13px;">{stripe_subscription_id or "N/A"}</div>

    <hr>
    <div class="footer">
      LGPD Sentinel AI · Notificação automática de assinatura<br>
      <a href="https://dashboard.stripe.com/customers" style="color:#6366f1;">
        Ver no Stripe Dashboard →
      </a>
    </div>
  </div>
</body>
</html>
"""
    msg.attach(MIMEText(html, "html"))
    return msg


def _build_cancellation_email(
    to_email: str,
    stripe_customer_id: str,
    api_key: Optional[str],
) -> MIMEMultipart:
    """Compose HTML email for subscription cancellation."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "⚠️ Assinatura cancelada — LGPD Sentinel AI"
    msg["To"] = to_email

    timestamp = datetime.utcnow().strftime("%d/%m/%Y às %H:%M UTC")

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
    .card {{ background: white; border-radius: 8px; padding: 30px; max-width: 600px;
             margin: 0 auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .badge {{ display: inline-block; background: #ef4444; color: white;
              padding: 4px 12px; border-radius: 20px; font-size: 13px; }}
    .label {{ color: #6b7280; font-size: 13px; margin-top: 16px; }}
    .value {{ color: #111827; font-size: 15px; font-weight: bold; margin-top: 2px; }}
    .footer {{ margin-top: 24px; font-size: 12px; color: #9ca3af; }}
    hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
  </style>
</head>
<body>
  <div class="card">
    <h2 style="color:#111827; margin-top:0;">🛡️ LGPD Sentinel AI</h2>
    <span class="badge">Assinatura cancelada</span>
    <p style="color:#374151; margin-top:16px;">
      Um assinante <strong>cancelou</strong> o plano Pro. O plano foi rebaixado para free.
    </p>
    <hr>
    <div class="label">📅 Data/hora</div>
    <div class="value">{timestamp}</div>

    <div class="label">🏷️ Stripe Customer ID</div>
    <div class="value" style="font-family:monospace;font-size:13px;">{stripe_customer_id}</div>

    <div class="label">🔑 API Key rebaixada</div>
    <div class="value" style="font-family:monospace;font-size:13px;">
      {(api_key[:20] + "...") if api_key else "Não encontrada"}
    </div>

    <hr>
    <div class="footer">
      LGPD Sentinel AI · Notificação automática de cancelamento<br>
      <a href="https://dashboard.stripe.com/customers/{stripe_customer_id}" style="color:#6366f1;">
        Ver cliente no Stripe →
      </a>
    </div>
  </div>
</body>
</html>
"""
    msg.attach(MIMEText(html, "html"))
    return msg


def send_notification(
    msg: MIMEMultipart,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    from_email: str,
    to_email: str,
) -> bool:
    """
    Send an email via SMTP. Returns True on success, False on failure.
    Never raises — caller is never blocked by email errors.
    """
    if not smtp_user or not smtp_password:
        logger.warning(
            "Email notification skipped: SMTP_USER or SMTP_PASSWORD not configured."
        )
        return False

    msg["From"] = from_email or smtp_user

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        logger.info("Email notification sent to %s (subject: %s)", to_email, msg["Subject"])
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP auth failed for %s. Check SMTP_USER / SMTP_PASSWORD in .env.", smtp_user
        )
    except smtplib.SMTPException as exc:
        logger.error("SMTP error sending notification: %s", exc)
    except OSError as exc:
        logger.error("Network error reaching SMTP server %s:%s — %s", smtp_host, smtp_port, exc)
    return False


def notify_new_subscriber(
    *,
    customer_email: Optional[str],
    api_key: str,
    plan: str,
    stripe_customer_id: Optional[str],
    stripe_subscription_id: Optional[str],
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    notification_email: str,
    from_email: str = "",
) -> bool:
    """Send 'new Pro subscriber' notification email. Returns True on success."""
    msg = _build_new_subscriber_email(
        to_email=notification_email,
        customer_email=customer_email,
        api_key=api_key,
        plan=plan,
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
    )
    return send_notification(
        msg=msg,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        from_email=from_email,
        to_email=notification_email,
    )


def notify_cancellation(
    *,
    stripe_customer_id: str,
    api_key: Optional[str],
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    notification_email: str,
    from_email: str = "",
) -> bool:
    """Send 'subscription cancelled' notification email. Returns True on success."""
    msg = _build_cancellation_email(
        to_email=notification_email,
        stripe_customer_id=stripe_customer_id,
        api_key=api_key,
    )
    return send_notification(
        msg=msg,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        from_email=from_email,
        to_email=notification_email,
    )
