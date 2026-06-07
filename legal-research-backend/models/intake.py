from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class IntakePlan(str, Enum):
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"
    consultation = "consultation"


class IntakeUrgency(str, Enum):
    standard = "standard"
    expedited = "expedited"
    urgent = "urgent"


class LegalResearchIntake(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    firm_name: str = Field(..., min_length=2, max_length=200)
    firm_size: Optional[str] = Field(None, max_length=50)
    plan: IntakePlan = IntakePlan.consultation
    jurisdiction: str = Field(..., min_length=2, max_length=200)
    practice_area: str = Field(..., min_length=2, max_length=200)
    case_count: Optional[int] = Field(None, ge=1, le=10000)
    research_question: str = Field(..., min_length=20, max_length=5000)
    urgency: IntakeUrgency = IntakeUrgency.standard
    has_documents: bool = False
    preferred_contact: str = Field(default="email", max_length=20)
    referral_source: Optional[str] = Field(None, max_length=200)
    demo_viewed: bool = False

    @field_validator("full_name", "firm_name", "jurisdiction", "practice_area", "research_question")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip()


class IntakeResponse(BaseModel):
    success: bool
    intake_id: str
    message: str
    next_steps: list[str]
    submitted_at: str


class IntakeRecord(LegalResearchIntake):
    intake_id: str
    submitted_at: str
    status: str = "received"
    notification_sent: bool = False
    nurture_stage: int = 0
    nurture_day0_sent: bool = False
    nurture_last_sent_at: Optional[str] = None
    nurture_opt_out: bool = False
