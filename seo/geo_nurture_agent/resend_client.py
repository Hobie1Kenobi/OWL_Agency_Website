"""Send transactional nurture emails via Resend."""

from __future__ import annotations

import httpx

from . import config


def send_email(
    to: str,
    subject: str,
    html: str,
    text: str,
    *,
    reply_to: str | None = None,
    tags: list[dict] | None = None,
) -> tuple[bool, str]:
    if not config.RESEND_API_KEY:
        return False, "RESEND_API_KEY not configured"

    payload: dict = {
        "from": config.NURTURE_FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "html": html,
        "text": text,
    }
    if reply_to:
        payload["reply_to"] = reply_to
    if tags:
        payload["tags"] = tags

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {config.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if response.status_code in (200, 201):
            data = response.json()
            return True, data.get("id", "sent")
        return False, f"Resend {response.status_code}: {response.text[:200]}"
    except httpx.HTTPError as exc:
        return False, str(exc)
