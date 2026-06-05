"""OWL AI Agency — Multi-Agent Paralegal Research API."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.orchestrator import ParalegalOrchestrator
from data import load_case
from models.intake import IntakeResponse, LegalResearchIntake
from services.intake_service import get_intake, submit_intake
from services.legal_sources import list_public_sources

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://owl-ai-agency.com,https://hobie1kenobi.github.io,http://localhost:8000,http://127.0.0.1:5500,http://localhost:5500",
).split(",")

app = FastAPI(
    title="OWL Legal Research API",
    description="Multi-agent paralegal system — Carpenter v. United States demo",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = ParalegalOrchestrator()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "owl-legal-research-api"}


@app.get("/api/sources")
async def get_sources():
    """Public legal data systems available without API keys."""
    return {"sources": list_public_sources()}


@app.get("/api/cases")
async def get_cases():
    case = load_case("carpenter_v_us")
    return {
        "cases": [
            {
                "id": case["case_id"],
                "name": case["full_name"],
                "citation": case["citation"],
                "court": case["court"],
                "summary": case["holding"][:200],
                "demo_available": True,
            }
        ]
    }


@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    if case_id != "carpenter_v_us":
        return {"error": "Case not found. Demo case: carpenter_v_us"}
    return load_case(case_id)


@app.post("/api/demo/run")
async def run_demo():
    """Execute the full six-agent paralegal pipeline on Carpenter v. United States."""
    result = await orchestrator.run_demo("carpenter_v_us")
    return result


@app.get("/api/demo/run")
async def run_demo_get():
    """GET alias for easy testing and keep-alive pings."""
    return await run_demo()


@app.post("/api/intake", response_model=IntakeResponse)
async def create_intake(payload: LegalResearchIntake):
    """Submit a legal research service intake request."""
    return await submit_intake(payload)


@app.get("/api/intake/{intake_id}")
async def read_intake(intake_id: str):
    """Look up intake status by reference number."""
    record = get_intake(intake_id)
    if not record:
        return {"error": "Intake not found", "intake_id": intake_id}
    return {
        "intake_id": record["intake_id"],
        "status": record.get("status", "received"),
        "submitted_at": record["submitted_at"],
        "plan": record["plan"],
        "firm_name": record["firm_name"],
    }
