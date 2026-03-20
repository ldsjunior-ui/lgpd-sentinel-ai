# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Unit tests for the email notification system (src/core/notifications.py).
SMTP calls are mocked — no real emails are sent.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from unittest.mock import MagicMock, patch


from src.core.notifications import (
    _build_new_subscriber_email,
    _build_cancellation_email,
    send_notification,
    notify_new_subscriber,
    notify_cancellation,
)

# ---------------------------------------------------------------------------
# Shared SMTP config for tests
# ---------------------------------------------------------------------------

SMTP_KWARGS = dict(
    smtp_host="smtp-mail.outlook.com",
    smtp_port=587,
    smtp_user="test@hotmail.com",
    smtp_password="secret123",
    notification_email="leo.jr_souza@hotmail.com",
    from_email="test@hotmail.com",
)

# ---------------------------------------------------------------------------
# _build_new_subscriber_email
# ---------------------------------------------------------------------------


def test_build_new_subscriber_email_has_required_fields():
    msg = _build_new_subscriber_email(
        to_email="leo.jr_souza@hotmail.com",
        customer_email="cliente@empresa.com.br",
        api_key="lgpd_abc123xyz",
        plan="pro",
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test456",
    )
    html_part = msg.get_payload(0).get_payload(decode=True).decode("utf-8")
    assert "cliente@empresa.com.br" in html_part
    assert "PRO" in html_part
    assert "lgpd_abc123xyz"[:20] in html_part
    assert "cus_test123" in html_part
    assert "sub_test456" in html_part


def test_build_new_subscriber_email_subject():
    msg = _build_new_subscriber_email(
        to_email="leo.jr_souza@hotmail.com",
        customer_email=None,
        api_key="lgpd_xyz",
        plan="pro",
        stripe_customer_id=None,
        stripe_subscription_id=None,
    )
    assert "Novo assinante Pro" in msg["Subject"]
    assert "LGPD Sentinel AI" in msg["Subject"]


def test_build_new_subscriber_email_handles_none_customer_email():
    msg = _build_new_subscriber_email(
        to_email="leo.jr_souza@hotmail.com",
        customer_email=None,
        api_key="lgpd_xyz",
        plan="pro",
        stripe_customer_id="cus_abc",
        stripe_subscription_id="sub_abc",
    )
    html_part = msg.get_payload(0).get_payload(decode=True).decode("utf-8")
    assert "Não informado" in html_part


# ---------------------------------------------------------------------------
# _build_cancellation_email
# ---------------------------------------------------------------------------


def test_build_cancellation_email_subject():
    msg = _build_cancellation_email(
        to_email="leo.jr_souza@hotmail.com",
        stripe_customer_id="cus_cancel123",
        api_key="lgpd_abc",
    )
    assert "cancelada" in msg["Subject"].lower()
    assert "LGPD Sentinel AI" in msg["Subject"]


def test_build_cancellation_email_has_customer_id():
    msg = _build_cancellation_email(
        to_email="leo.jr_souza@hotmail.com",
        stripe_customer_id="cus_cancel123",
        api_key=None,
    )
    html_part = msg.get_payload(0).get_payload(decode=True).decode("utf-8")
    assert "cus_cancel123" in html_part


def test_build_cancellation_email_handles_none_api_key():
    msg = _build_cancellation_email(
        to_email="leo.jr_souza@hotmail.com",
        stripe_customer_id="cus_cancel123",
        api_key=None,
    )
    html_part = msg.get_payload(0).get_payload(decode=True).decode("utf-8")
    assert "Não encontrada" in html_part


# ---------------------------------------------------------------------------
# send_notification
# ---------------------------------------------------------------------------


def test_send_notification_returns_false_when_no_credentials():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test"
    result = send_notification(
        msg=msg,
        smtp_host="smtp.host.com",
        smtp_port=587,
        smtp_user="",         # empty — no credentials
        smtp_password="",
        from_email="",
        to_email="leo.jr_souza@hotmail.com",
    )
    assert result is False


def test_send_notification_success():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test"

    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
    mock_smtp.__exit__ = MagicMock(return_value=False)

    with patch("smtplib.SMTP", return_value=mock_smtp):
        result = send_notification(
            msg=msg,
            smtp_host="smtp-mail.outlook.com",
            smtp_port=587,
            smtp_user="test@hotmail.com",
            smtp_password="secret",
            from_email="test@hotmail.com",
            to_email="leo.jr_souza@hotmail.com",
        )

    assert result is True
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once_with("test@hotmail.com", "secret")
    mock_smtp.sendmail.assert_called_once()


def test_send_notification_returns_false_on_auth_error():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test"

    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
    mock_smtp.__exit__ = MagicMock(return_value=False)
    mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")

    with patch("smtplib.SMTP", return_value=mock_smtp):
        result = send_notification(
            msg=msg,
            smtp_host="smtp-mail.outlook.com",
            smtp_port=587,
            smtp_user="test@hotmail.com",
            smtp_password="wrong_password",
            from_email="test@hotmail.com",
            to_email="leo.jr_souza@hotmail.com",
        )

    assert result is False  # never raises — just returns False


def test_send_notification_returns_false_on_network_error():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test"

    with patch("smtplib.SMTP", side_effect=OSError("Connection refused")):
        result = send_notification(
            msg=msg,
            smtp_host="unreachable.host.com",
            smtp_port=587,
            smtp_user="test@hotmail.com",
            smtp_password="secret",
            from_email="test@hotmail.com",
            to_email="leo.jr_souza@hotmail.com",
        )

    assert result is False  # never raises


# ---------------------------------------------------------------------------
# notify_new_subscriber (high-level)
# ---------------------------------------------------------------------------


def test_notify_new_subscriber_calls_smtp():
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
    mock_smtp.__exit__ = MagicMock(return_value=False)

    with patch("smtplib.SMTP", return_value=mock_smtp):
        result = notify_new_subscriber(
            customer_email="novo@cliente.com.br",
            api_key="lgpd_newkey123",
            plan="pro",
            stripe_customer_id="cus_new123",
            stripe_subscription_id="sub_new456",
            **SMTP_KWARGS,
        )

    assert result is True
    mock_smtp.sendmail.assert_called_once()
    # Verify it was sent to the notification email
    sendmail_call = mock_smtp.sendmail.call_args
    assert sendmail_call[0][1] == "leo.jr_souza@hotmail.com"


def test_notify_new_subscriber_email_content():
    """Verify the email body contains subscriber details."""
    import email as _email
    from email.header import decode_header
    sent_emails = []

    def capture_sendmail(from_addr, to_addrs, msg_str):
        sent_emails.append(msg_str)

    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
    mock_smtp.__exit__ = MagicMock(return_value=False)
    mock_smtp.sendmail.side_effect = capture_sendmail

    with patch("smtplib.SMTP", return_value=mock_smtp):
        notify_new_subscriber(
            customer_email="cliente@empresa.com.br",
            api_key="lgpd_abc123xyz456789",
            plan="pro",
            stripe_customer_id="cus_xyz",
            stripe_subscription_id="sub_xyz",
            **SMTP_KWARGS,
        )

    assert len(sent_emails) == 1
    parsed = _email.message_from_string(sent_emails[0])
    html_body = parsed.get_payload(0).get_payload(decode=True).decode("utf-8")
    raw_subj = decode_header(parsed["Subject"])
    subject = "".join(s.decode(enc or "utf-8") if isinstance(s, bytes) else s for s, enc in raw_subj)
    assert "cliente@empresa.com.br" in html_body
    assert "Novo assinante Pro" in subject


# ---------------------------------------------------------------------------
# notify_cancellation (high-level)
# ---------------------------------------------------------------------------


def test_notify_cancellation_calls_smtp():
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
    mock_smtp.__exit__ = MagicMock(return_value=False)

    with patch("smtplib.SMTP", return_value=mock_smtp):
        result = notify_cancellation(
            stripe_customer_id="cus_cancelled123",
            api_key="lgpd_old_key",
            **SMTP_KWARGS,
        )

    assert result is True
    mock_smtp.sendmail.assert_called_once()


def test_notify_cancellation_email_subject():
    import email as _email
    from email.header import decode_header
    sent_emails = []

    def capture_sendmail(from_addr, to_addrs, msg_str):
        sent_emails.append(msg_str)

    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
    mock_smtp.__exit__ = MagicMock(return_value=False)
    mock_smtp.sendmail.side_effect = capture_sendmail

    with patch("smtplib.SMTP", return_value=mock_smtp):
        notify_cancellation(
            stripe_customer_id="cus_cancelled123",
            api_key=None,
            **SMTP_KWARGS,
        )

    assert len(sent_emails) == 1
    parsed = _email.message_from_string(sent_emails[0])
    raw_subj = decode_header(parsed["Subject"])
    subject = "".join(s.decode(enc or "utf-8") if isinstance(s, bytes) else s for s, enc in raw_subj)
    assert "cancelada" in subject.lower() or "cancelamento" in subject.lower()
