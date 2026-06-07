"""Send editor/tip emails via Zoho — no portal account on target site."""

from __future__ import annotations

import os
import smtplib
import time
from email.mime.text import MIMEText

from . import config


def _build_tip_body(profile: dict) -> str:
    site = config.SITE_URL
    return f"""Hi,

{profile['sender_name']}, founder of {profile['company_name']}, has a legal-tech story that may fit your audience.

We built a six-agent paralegal research system that verifies live public legal databases (Cornell LII, Oyez, CourtListener, GovInfo) and produces filing-ready memos with Bluebook citations—not a generic chatbot.

Public demo (Carpenter v. United States, 12 live sources):
{profile['demo_url']}

Comparison guides for your readers:
{site}/compare/owl-vs-chatgpt-legal-research.html
{site}/compare/owl-vs-manual-legal-research.html

Happy to provide a short guest post, quote, or demo walkthrough.

Best,
{profile['sender_name']}
{profile['sender_title']}, {profile['company_name']}
{profile['sender_email']} | {profile['phone']}
"""


def send_tip_email(platform: dict, *, dry_run: bool = False) -> dict:
    if not config.ZOHO_APP_PASSWORD:
        return {"skipped": True, "reason": "ZOHO_APP_PASSWORD not set"}

    profile = config.load_profile()
    to = platform["to"]
    subject = platform.get("subject_template", "Legal tech story tip — OWL AI Agency")
    body = _build_tip_body(profile)

    if dry_run:
        return {"dry_run": True, "to": to, "subject": subject, "body_preview": body[:200]}

    host = os.getenv("ZOHO_SMTP_HOST", "smtp.zoho.com")
    port = int(os.getenv("ZOHO_SMTP_PORT", "587"))
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = config.ZOHO_FROM
    msg["To"] = to

    try:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(config.ZOHO_FROM, config.ZOHO_APP_PASSWORD)
            smtp.sendmail(config.ZOHO_FROM, [to], msg.as_string())
        return {"ok": True, "to": to, "subject": subject}
    except smtplib.SMTPException as e:
        return {"ok": False, "to": to, "error": str(e)}


def run_email_tips(*, dry_run: bool = False, delay: int | None = None) -> list[dict]:
    registry = config.load_registry()
    wait = delay if delay is not None else config.TRAFFIC_EMAIL_DELAY
    platforms = [
        p for p in registry["platforms"]
        if p.get("tier") == "email_no_account" and p.get("action") == "email_tip"
    ]
    results = []
    for i, platform in enumerate(platforms):
        if i > 0 and not dry_run:
            time.sleep(wait)
        result = send_tip_email(platform, dry_run=dry_run)
        result["platform_id"] = platform["id"]
        results.append(result)
    return results
