from __future__ import annotations

from pydantic import BaseModel, Field


class VerifyCitationsRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=80_000)
    matter_id: str | None = Field(default=None, max_length=80)
