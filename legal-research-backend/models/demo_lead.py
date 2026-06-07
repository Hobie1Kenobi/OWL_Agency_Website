from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class DemoLeadSubmit(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=120)
    firm_name: Optional[str] = Field(None, max_length=200)


class DemoLeadResponse(BaseModel):
    success: bool
    lead_id: str
    message: str
