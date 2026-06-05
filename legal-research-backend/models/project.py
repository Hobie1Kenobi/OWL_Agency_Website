from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class PaymentIntentRequest(BaseModel):
    intake_id: str = Field(..., min_length=8, max_length=40)
    plan: str = Field(..., pattern="^(starter|professional|enterprise)$")


class PaymentConfirmRequest(BaseModel):
    intake_id: str = Field(..., min_length=8, max_length=40)
    payment_intent_id: str = Field(..., min_length=8, max_length=80)


class ResearchQueryRequest(BaseModel):
    case_name: str = Field(..., min_length=3, max_length=300)
    jurisdiction: str = Field(..., min_length=2, max_length=200)
    practice_area: str = Field(..., min_length=2, max_length=200)
    research_question: str = Field(..., min_length=20, max_length=5000)
    desired_deliverables: list[str] = Field(default_factory=list)
    key_facts: Optional[str] = Field(None, max_length=3000)
    relief_sought: Optional[str] = Field(None, max_length=1000)


class ProjectResponse(BaseModel):
    access_token: str
    intake_id: str
    plan: str
    tier: dict[str, Any]
    firm_name: str
    contact_name: str
    contact_email: str
    status: str
    cases_used: int
    cases_remaining: int
    research_jobs: list[dict[str, Any]]
    onboarding_steps: list[dict[str, Any]]
    api_key: Optional[str] = None
    workspace_url: str
