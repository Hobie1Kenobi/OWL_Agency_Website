"""Day-0 nurture email for new intake submissions (Resend)."""

from __future__ import annotations

import os

import httpx

PLAN_LABELS = {
    "starter": "Starter ($3,000)",
    "professional": "Professional ($6,000)",
    "enterprise": "Enterprise ($12,000)",
    "consultation": "Free Consultation",
}

DEMO_URL = "https://owl-ai-agency.com/legal-research-demo.html?autostart=1"
PRODUCT_URL = "https://owl-ai-agency.com/legal-research.html"


def _first_name(full_name: str) -> str:
    return full_name.strip().split()[0] if full_name.strip() else "there"


def build_day0_email(record: dict) -> tuple[str, str, str]:
    name = _first_name(record["full_name"])
    firm = record.get("firm_name", "your firm")
    intake_id = record["intake_id"]
    plan = PLAN_LABELS.get(record.get("plan", "consultation"), record.get("plan", "consultation"))

    subject = f"Welcome to OWL Legal Research — your next steps (Ref {intake_id})"
    text = (
        f"Hi {name},\n\n"
        f"Thank you for submitting your OWL Legal Research intake for {firm}. "
        f"Your reference is {intake_id} and your selected plan is {plan}.\n\n"
        f"While our team reviews your submission (within one business day), "
        f"watch the live Carpenter v. United States demo:\n{DEMO_URL}\n\n"
        f"Next steps:\n"
        f"1. Save your reference number: {intake_id}\n"
        f"2. Review the demo output format\n"
        f"3. Expect a scoped proposal with timeline and deliverables\n\n"
        f"Questions? Reply to this email.\n\n"
        f"— Hobie Cunningham, OWL AI Agency"
    )
    html = (
        f"<p>Hi {name},</p>"
        f"<p>Thank you for submitting your OWL Legal Research intake for <strong>{firm}</strong>. "
        f"Your reference is <strong>{intake_id}</strong> and your selected plan is {plan}.</p>"
        f"<p>While our team reviews your submission (within one business day), "
        f'<a href="{DEMO_URL}">watch the live Carpenter v. United States demo</a>.</p>'
        f"<p><strong>Next steps:</strong></p><ol>"
        f"<li>Save your reference number: {intake_id}</li>"
        f"<li>Review the demo output format</li>"
        f"<li>Expect a scoped proposal with timeline and deliverables</li>"
        f"</ol>"
        f'<p><a href="{PRODUCT_URL}#intake">View intake portal</a></p>'
        f"<p>— Hobie Cunningham, OWL AI Agency</p>"
    )
    return subject, html, text


async def send_day0_nurture(record: dict) -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv(
        "NURTURE_FROM_EMAIL",
        os.getenv("INTAKE_FROM_EMAIL", "OWL Legal Research <onboarding@resend.dev>"),
    )
    if not api_key:
        return False

    subject, html, text = build_day0_email(record)
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
                    "tags": [{"name": "nurture_stage", "value": "0"}],
                },
            )
            return response.status_code in (200, 201)
    except httpx.HTTPError:
        return False
