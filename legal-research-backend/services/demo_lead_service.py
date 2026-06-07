"""Capture demo viewers for nurture without full intake."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

from models.demo_lead import DemoLeadResponse, DemoLeadSubmit

DEMO_LEADS_DIR = Path(__file__).resolve().parent.parent / "data" / "demo_leads"
DEMO_URL = "https://owl-ai-agency.com/legal-research-demo.html?autostart=1"
PRODUCT_URL = "https://owl-ai-agency.com/legal-research.html"


def _ensure_storage() -> None:
    DEMO_LEADS_DIR.mkdir(parents=True, exist_ok=True)


def _first_name(full_name: str | None) -> str:
    if not full_name or not full_name.strip():
        return "there"
    return full_name.strip().split()[0]


async def _send_demo_welcome_email(record: dict) -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv(
        "NURTURE_FROM_EMAIL",
        os.getenv("INTAKE_FROM_EMAIL", "OWL Legal Research <onboarding@resend.dev>"),
    )
    if not api_key:
        return False

    name = _first_name(record.get("full_name"))
    subject = "Your OWL legal research demo — next steps"
    text = (
        f"Hi {name},\n\n"
        f"Thanks for watching the Carpenter v. United States demo. "
        f"You saw OWL's six agents verify live legal sources and produce filing-ready documents.\n\n"
        f"Re-run anytime: {DEMO_URL}\n\n"
        f"Ready to scope your firm's matters? Free consultation: {PRODUCT_URL}#intake\n\n"
        f"— Hobie Cunningham, OWL AI Agency"
    )
    html = (
        f"<p>Hi {name},</p>"
        f"<p>Thanks for watching the <strong>Carpenter v. United States</strong> demo.</p>"
        f'<p><a href="{DEMO_URL}">Re-run the demo</a> · '
        f'<a href="{PRODUCT_URL}#intake">Book free consultation</a></p>'
        f"<p>— Hobie Cunningham, OWL AI Agency</p>"
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "from": from_email,
                    "to": [record["email"]],
                    "subject": subject,
                    "html": html,
                    "text": text,
                    "tags": [{"name": "nurture_stage", "value": "demo_0"}],
                },
            )
            return response.status_code in (200, 201)
    except httpx.HTTPError:
        return False


async def submit_demo_lead(payload: DemoLeadSubmit) -> DemoLeadResponse:
    _ensure_storage()
    lead_id = f"DEMO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    submitted_at = datetime.now(timezone.utc).isoformat()

    record = {
        "lead_id": lead_id,
        "email": str(payload.email),
        "full_name": payload.full_name,
        "firm_name": payload.firm_name,
        "source": "demo",
        "submitted_at": submitted_at,
        "demo_viewed": True,
        "nurture_stage": 0,
        "nurture_day0_sent": False,
        "nurture_opt_out": False,
    }

    welcome_sent = await _send_demo_welcome_email(record)
    if welcome_sent:
        record["nurture_day0_sent"] = True
        record["nurture_stage"] = 1
        record["nurture_last_sent_at"] = submitted_at

    path = DEMO_LEADS_DIR / f"{lead_id}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    name = _first_name(payload.full_name)
    return DemoLeadResponse(
        success=True,
        lead_id=lead_id,
        message=f"Thanks, {name}! Check your inbox for demo follow-up steps.",
    )
