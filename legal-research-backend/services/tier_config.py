"""Paid tier definitions — single source of truth for entitlements."""

from __future__ import annotations

from typing import Any

TIER_CONFIG: dict[str, dict[str, Any]] = {
    "starter": {
        "id": "starter",
        "name": "Starter Package",
        "price_cents": 300_000,
        "price_display": "$3,000",
        "case_limit": 25,
        "turnaround_hours": 72,
        "documents": [
            "legal_research_memorandum",
            "case_brief",
            "table_of_authorities",
        ],
        "document_labels": {
            "legal_research_memorandum": "Research Memorandum",
            "case_brief": "Case Brief (IRAC)",
            "table_of_authorities": "Table of Authorities",
        },
        "excel_export": "basic",
        "custom_branding": False,
        "api_access": False,
        "research_runs_per_month": 25,
        "features": [
            "Up to 25 case research runs",
            "Research memo, case brief & table of authorities",
            "Basic CSV case summary export",
            "72-hour turnaround SLA",
            "Six-agent paralegal pipeline",
            "Live public source verification",
        ],
    },
    "professional": {
        "id": "professional",
        "name": "Professional Package",
        "price_cents": 600_000,
        "price_display": "$6,000",
        "case_limit": 75,
        "turnaround_hours": 48,
        "documents": [
            "legal_research_memorandum",
            "case_brief",
            "motion_to_suppress",
            "appellate_brief_excerpt",
            "table_of_authorities",
            "certificate_of_service",
        ],
        "document_labels": {
            "legal_research_memorandum": "Research Memorandum",
            "case_brief": "Case Brief (IRAC)",
            "motion_to_suppress": "Motion to Suppress",
            "appellate_brief_excerpt": "Appellate Brief Excerpt",
            "table_of_authorities": "Table of Authorities",
            "certificate_of_service": "Certificate of Service",
        },
        "excel_export": "interactive",
        "custom_branding": True,
        "api_access": False,
        "research_runs_per_month": 75,
        "features": [
            "Up to 75 case research runs",
            "Full six-document paralegal package",
            "Interactive CSV precedent matrix export",
            "48-hour turnaround SLA",
            "Custom firm branding on deliverables",
            "Priority support queue",
        ],
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise Package",
        "price_cents": 1_200_000,
        "price_display": "$12,000",
        "case_limit": 999_999,
        "turnaround_hours": 24,
        "documents": [
            "legal_research_memorandum",
            "case_brief",
            "motion_to_suppress",
            "appellate_brief_excerpt",
            "table_of_authorities",
            "certificate_of_service",
        ],
        "document_labels": {
            "legal_research_memorandum": "Research Memorandum",
            "case_brief": "Case Brief (IRAC)",
            "motion_to_suppress": "Motion to Suppress",
            "appellate_brief_excerpt": "Appellate Brief Excerpt",
            "table_of_authorities": "Table of Authorities",
            "certificate_of_service": "Certificate of Service",
        },
        "excel_export": "advanced",
        "custom_branding": True,
        "api_access": True,
        "research_runs_per_month": 999_999,
        "features": [
            "Unlimited case research runs",
            "Premium templates & white-label branding",
            "Advanced CSV + visualization data export",
            "24-hour turnaround SLA",
            "REST API access with dedicated key",
            "Dedicated priority queue",
        ],
    },
}


def get_tier(plan: str) -> dict[str, Any] | None:
    return TIER_CONFIG.get(plan)


def is_paid_plan(plan: str) -> bool:
    return plan in TIER_CONFIG


def public_tier_summary(plan: str) -> dict[str, Any]:
    tier = get_tier(plan)
    if not tier:
        return {}
    return {
        "id": tier["id"],
        "name": tier["name"],
        "price_display": tier["price_display"],
        "case_limit": tier["case_limit"],
        "turnaround_hours": tier["turnaround_hours"],
        "documents": tier["documents"],
        "document_labels": tier["document_labels"],
        "excel_export": tier["excel_export"],
        "custom_branding": tier["custom_branding"],
        "api_access": tier["api_access"],
        "features": tier["features"],
    }
