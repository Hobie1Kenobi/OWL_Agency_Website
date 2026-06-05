"""Persist and notify on legal research intake submissions."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

from models.intake import IntakeRecord, IntakeResponse, LegalResearchIntake

INTAKE_DIR = Path(__file__).resolve().parent.parent / "data" / "intakes"
PLAN_LABELS = {
    "starter": "Starter ($3,000)",
    "professional": "Professional ($6,000)",
    "enterprise": "Enterprise ($12,000)",
    "consultation": "Free Consultation",
}
URGENCY_LABELS = {
    "standard": "Standard turnaround",
    "expedited": "Expedited (48hr)",
    "urgent": "Urgent (24hr)",
}


def _ensure_storage() -> None:
    INTAKE_DIR.mkdir(parents=True, exist_ok=True)


def _save_record(record: IntakeRecord) -> None:
    _ensure_storage()
    path = INTAKE_DIR / f"{record.intake_id}.json"
    path.write_text(record.model_dump_json(indent=2), encoding="utf-8")


async def _send_notification(record: IntakeRecord) -> bool:
    """Send team notification via Resend if configured."""
    api_key = os.getenv("RESEND_API_KEY")
    notify_to = os.getenv("INTAKE_NOTIFY_EMAIL", "sales@owl-ai-agency.com")
    from_email = os.getenv("INTAKE_FROM_EMAIL", "OWL Legal Research <onboarding@resend.dev>")

    if not api_key:
        return False

    plan = PLAN_LABELS.get(record.plan.value, record.plan.value)
    urgency = URGENCY_LABELS.get(record.urgency.value, record.urgency.value)
    body = f"""New Legal Research Intake — {record.intake_id}

Contact: {record.full_name} <{record.email}>
Phone: {record.phone or 'Not provided'}
Firm: {record.firm_name}
Firm size: {record.firm_size or 'Not provided'}

Plan: {plan}
Urgency: {urgency}
Jurisdiction: {record.jurisdiction}
Practice area: {record.practice_area}
Estimated cases: {record.case_count or 'Not specified'}
Has documents ready: {'Yes' if record.has_documents else 'No'}
Demo viewed: {'Yes' if record.demo_viewed else 'No'}
Preferred contact: {record.preferred_contact}
Referral: {record.referral_source or 'Not specified'}

Research question:
{record.research_question}

Submitted: {record.submitted_at}
"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "from": from_email,
                    "to": [notify_to],
                    "subject": f"[OWL Intake] {record.firm_name} — {plan}",
                    "text": body,
                },
            )
            return response.status_code in (200, 201)
    except httpx.HTTPError:
        return False


async def submit_intake(payload: LegalResearchIntake) -> IntakeResponse:
    intake_id = f"OWL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    submitted_at = datetime.now(timezone.utc).isoformat()

    record = IntakeRecord(
        **payload.model_dump(),
        intake_id=intake_id,
        submitted_at=submitted_at,
    )

    notification_sent = await _send_notification(record)
    record.notification_sent = notification_sent
    _save_record(record)

    plan_label = PLAN_LABELS.get(payload.plan.value, payload.plan.value)
    next_steps = [
        f"Your reference number is {intake_id} — save it for follow-up.",
        "Our legal research team will review your submission within one business day.",
        "You'll receive a scoped proposal with timeline and deliverables.",
    ]
    if payload.plan.value != "consultation":
        next_steps.append("After proposal approval, proceed to payment to start your research project.")

    return IntakeResponse(
        success=True,
        intake_id=intake_id,
        message=f"Thank you, {payload.full_name.split()[0]}! Your {plan_label} intake was received.",
        next_steps=next_steps,
        submitted_at=submitted_at,
    )


def get_intake(intake_id: str) -> dict | None:
    path = INTAKE_DIR / f"{intake_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
