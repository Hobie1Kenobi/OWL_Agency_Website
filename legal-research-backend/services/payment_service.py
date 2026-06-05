"""Stripe PaymentIntent integration for legal research tiers."""

from __future__ import annotations

import os
from typing import Any

import stripe

from services.intake_service import get_intake, update_intake
from services.project_service import activate_project_for_intake
from services.tier_config import get_tier, is_paid_plan

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


def _stripe_configured() -> bool:
    key = os.getenv("STRIPE_SECRET_KEY", "")
    return bool(key and not key.startswith("sk_test_your") and not key.startswith("sk_live_your"))


def get_publishable_key() -> str | None:
    key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    if key and "your_publishable" not in key:
        return key
    return None


async def create_payment_intent(intake_id: str, plan: str) -> dict[str, Any]:
    if not is_paid_plan(plan):
        return {"error": "Invalid plan", "detail": "Only starter, professional, and enterprise are paid tiers."}

    intake = get_intake(intake_id)
    if not intake:
        return {"error": "Intake not found", "intake_id": intake_id}

    if intake.get("plan") != plan:
        return {"error": "Plan mismatch", "detail": f"Intake plan is {intake.get('plan')}, not {plan}."}

    if intake.get("payment_status") == "paid":
        project = intake.get("project_access_token")
        return {
            "already_paid": True,
            "intake_id": intake_id,
            "access_token": project,
            "workspace_url": f"/legal-research-workspace.html?token={project}" if project else None,
        }

    tier = get_tier(plan)
    if not tier:
        return {"error": "Unknown tier"}

    if not _stripe_configured():
        return {
            "error": "Stripe not configured",
            "detail": "Add STRIPE_SECRET_KEY to server environment.",
        }

    intent = stripe.PaymentIntent.create(
        amount=tier["price_cents"],
        currency="usd",
        metadata={
            "intake_id": intake_id,
            "plan": plan,
            "firm_name": intake.get("firm_name", ""),
            "contact_email": intake.get("email", ""),
        },
        receipt_email=intake.get("email"),
        description=f"OWL Legal Research — {tier['name']}",
    )

    update_intake(intake_id, {
        "payment_status": "pending",
        "payment_intent_id": intent.id,
        "amount_cents": tier["price_cents"],
    })

    return {
        "client_secret": intent.client_secret,
        "payment_intent_id": intent.id,
        "amount_cents": tier["price_cents"],
        "amount_display": tier["price_display"],
        "plan": plan,
        "intake_id": intake_id,
    }


async def confirm_payment(intake_id: str, payment_intent_id: str) -> dict[str, Any]:
    intake = get_intake(intake_id)
    if not intake:
        return {"error": "Intake not found"}

    if intake.get("payment_status") == "paid" and intake.get("project_access_token"):
        return {
            "success": True,
            "already_paid": True,
            "access_token": intake["project_access_token"],
            "workspace_url": f"/legal-research-workspace.html?token={intake['project_access_token']}",
        }

    if not _stripe_configured():
        return {"error": "Stripe not configured"}

    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    if intent.metadata.get("intake_id") != intake_id:
        return {"error": "Payment does not match intake"}

    if intent.status != "succeeded":
        return {
            "error": "Payment not completed",
            "status": intent.status,
            "detail": "Payment must succeed before workspace access is granted.",
        }

    plan = intake.get("plan")
    project = activate_project_for_intake(intake_id, plan, payment_intent_id)

    update_intake(intake_id, {
        "payment_status": "paid",
        "status": "active",
        "project_access_token": project["access_token"],
        "paid_at": project["activated_at"],
    })

    return {
        "success": True,
        "access_token": project["access_token"],
        "workspace_url": f"/legal-research-workspace.html?token={project['access_token']}",
        "plan": plan,
        "tier_name": project["tier"]["name"],
    }
