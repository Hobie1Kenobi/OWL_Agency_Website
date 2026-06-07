"""Lead nurture sequences via Resend — intake subscribers and demo leads."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .resend_client import send_email

PLAN_LABELS = {
    "starter": "Starter ($3,000)",
    "professional": "Professional ($6,000)",
    "enterprise": "Enterprise ($12,000)",
    "consultation": "Free Consultation",
}


def _first_name(full_name: str) -> str:
    return full_name.strip().split()[0] if full_name.strip() else "there"


def _build_email(stage: int, lead: dict) -> tuple[str, str, str]:
    profile = config.load_company_profile()
    sequences = config.load_sequences()
    stage_meta = next((s for s in sequences["stages"] if s["stage"] == stage), None)
    if not stage_meta:
        raise ValueError(f"Unknown nurture stage: {stage}")

    name = _first_name(lead.get("full_name", ""))
    firm = lead.get("firm_name", "your firm")
    intake_id = lead.get("intake_id", "")
    plan = PLAN_LABELS.get(lead.get("plan", "consultation"), lead.get("plan", "consultation"))
    demo = profile["demo_url"]
    product = profile["product_page"]
    sender = profile["sender_name"]

    subject = stage_meta["subject"]
    if intake_id and stage == 0:
        subject = f"{subject} (Ref {intake_id})"

    bodies = {
        0: (
            f"Hi {name},\n\n"
            f"Thank you for submitting your OWL Legal Research intake for {firm}. "
            f"Your reference is {intake_id} and your selected plan is {plan}.\n\n"
            f"While our team reviews your submission (within one business day), "
            f"watch the live Carpenter v. United States demo:\n{demo}\n\n"
            f"Next steps:\n"
            f"1. Save your reference number: {intake_id}\n"
            f"2. Review the demo output format\n"
            f"3. Expect a scoped proposal with timeline and deliverables\n\n"
            f"Questions? Reply to this email or call {profile['phone']}.\n\n"
            f"— {sender}, {profile['company_name']}"
        ),
        1: (
            f"Hi {name},\n\n"
            f"Many firms evaluate OWL by running the public demo first. "
            f"It walks through Carpenter v. United States with six agents verifying "
            f"12 live legal sources—memos, briefs, and citations included.\n\n"
            f"Run the demo: {demo}\n\n"
            f"Key outputs your team will see:\n"
            f"• Research memo with verified authorities\n"
            f"• Case brief with precedent mapping\n"
            f"• Table of authorities in Bluebook format\n\n"
            f"When you're ready to scope your matters: {product}#intake\n\n"
            f"— {sender}"
        ),
        2: (
            f"Hi {name},\n\n"
            f"Paralegals often spend 4–8 hours per complex research matter on manual "
            f"source gathering and first-draft memos. OWL's six-agent pipeline compresses "
            f"that into a structured workspace run with live verification.\n\n"
            f"Package overview:\n"
            f"• Starter $3,000 — 25 runs, 72-hour SLA\n"
            f"• Professional $6,000 — 75 runs, 48-hour SLA\n"
            f"• Enterprise $12,000 — unlimited runs, 24-hour SLA\n\n"
            f"Compare packages: {product}#pricing\n"
            f"Your intake ref: {intake_id or 'not yet submitted'}\n\n"
            f"— {sender}"
        ),
        3: (
            f"Hi {name},\n\n"
            f"If you're still evaluating legal research automation for {firm}, "
            f"I'd welcome a 20-minute scoping call—no obligation.\n\n"
            f"We'll cover jurisdiction, practice area, document types, and which "
            f"package fits your caseload.\n\n"
            f"Book via intake (free consultation): {product}#intake\n"
            f"Or reply with two times that work for you.\n\n"
            f"Demo link (always available): {demo}\n\n"
            f"— {sender}\n{profile['sender_email']}"
        ),
    }

    text = bodies.get(stage, bodies[3])
    html = (
        f"<p>{text.replace(chr(10) + chr(10), '</p><p>').replace(chr(10), '<br>')}</p>"
        f'<p><a href="{demo}">Open live demo</a> · '
        f'<a href="{product}#intake">Start intake</a></p>'
    )
    return subject, html, text


def load_intake_records() -> list[dict]:
    records = []
    intake_dir = config.INTAKE_DIR
    if not intake_dir.exists():
        return records
    for path in sorted(intake_dir.glob("OWL-*.json")):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return records


def _days_since(iso_ts: str) -> float:
    submitted = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return (now - submitted).total_seconds() / 86400


def _eligible_stage(record: dict) -> int | None:
    if record.get("nurture_opt_out"):
        return None
    current = int(record.get("nurture_stage", 0))
    if current >= 4:
        return None
    days = _days_since(record["submitted_at"])
    delays = config.NURTURE_DELAYS_DAYS
    next_stage = current
    if next_stage == 0 and record.get("nurture_day0_sent"):
        next_stage = 1
    if next_stage not in delays:
        return None
    required = delays[next_stage]
    if days >= required:
        return next_stage
    return None


def send_stage_to_lead(lead: dict, stage: int, *, dry_run: bool = False) -> dict:
    if lead.get("nurture_opt_out"):
        return {"skipped": True, "reason": "opted out"}

    subject, html, text = _build_email(stage, lead)
    to = lead["email"]

    if dry_run:
        return {"dry_run": True, "to": to, "stage": stage, "subject": subject}

    ok, detail = send_email(
        to,
        subject,
        html,
        text,
        reply_to=config.load_company_profile()["sender_email"],
        tags=[{"name": "nurture_stage", "value": str(stage)}],
    )
    return {"ok": ok, "to": to, "stage": stage, "detail": detail}


def update_intake_nurture(intake_id: str, stage: int) -> None:
    path = config.INTAKE_DIR / f"{intake_id}.json"
    if not path.exists():
        return
    record = json.loads(path.read_text(encoding="utf-8"))
    record["nurture_stage"] = stage + 1
    record["nurture_last_sent_at"] = datetime.now(timezone.utc).isoformat()
    if stage == 0:
        record["nurture_day0_sent"] = True
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def run_due_sequences(*, dry_run: bool = False, confirm: bool = False) -> list[dict]:
    results = []
    for record in load_intake_records():
        stage = _eligible_stage(record)
        if stage is None:
            continue
        if stage == 0 and record.get("nurture_day0_sent"):
            continue
        result = send_stage_to_lead(record, stage, dry_run=dry_run or not confirm)
        result["intake_id"] = record["intake_id"]
        results.append(result)
        if result.get("ok") and confirm:
            update_intake_nurture(record["intake_id"], stage)
    return results


def list_nurture_queue() -> list[dict]:
    queue = []
    for record in load_intake_records():
        stage = _eligible_stage(record)
        queue.append(
            {
                "intake_id": record["intake_id"],
                "email": record["email"],
                "firm_name": record.get("firm_name"),
                "submitted_at": record["submitted_at"],
                "nurture_stage": record.get("nurture_stage", 0),
                "days_since_submit": round(_days_since(record["submitted_at"]), 1),
                "due_stage": stage,
            }
        )
    return queue


def ensure_leads_csv() -> None:
    if config.LEADS_FILE.exists():
        return
    with open(config.LEADS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["lead_id", "email", "full_name", "source", "created_at", "nurture_stage", "opt_out"]
        )


def run_nurture_command(command: str, **kwargs) -> None:
    ensure_leads_csv()
    if command == "queue":
        queue = list_nurture_queue()
        due = [q for q in queue if q["due_stage"] is not None]
        print(f"Intakes: {len(queue)} | Due now: {len(due)}")
        for item in due:
            print(
                f"  {item['intake_id']} -> stage {item['due_stage']} "
                f"({item['email']}, day {item['days_since_submit']})"
            )
    elif command == "preview":
        stage = int(kwargs.get("stage", 0))
        sample = {
            "full_name": "Jane Attorney",
            "firm_name": "Sample LLP",
            "intake_id": "OWL-20260605-SAMPLE",
            "plan": "consultation",
            "email": "preview@example.com",
        }
        subject, html, text = _build_email(stage, sample)
        print(f"Subject: {subject}\n\n{text}")
    elif command == "run":
        dry_run = kwargs.get("dry_run", True)
        confirm = kwargs.get("confirm", False)
        results = run_due_sequences(dry_run=dry_run, confirm=confirm)
        for r in results:
            print(json.dumps(r))
        sent = sum(1 for r in results if r.get("ok"))
        print(f"Processed {len(results)} | Sent {sent}")
    else:
        raise SystemExit(f"Unknown nurture command: {command}")
