"""OWL AI Agency — Multi-Agent Paralegal Research API."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
from fastapi.middleware.cors import CORSMiddleware

from agents.orchestrator import ParalegalOrchestrator
from data import load_case
from models.demo_lead import DemoLeadResponse, DemoLeadSubmit
from models.intake import IntakeResponse, LegalResearchIntake
from models.project import PaymentConfirmRequest, PaymentIntentRequest, ResearchQueryRequest
from services.demo_lead_service import submit_demo_lead
from services.intake_service import get_intake, submit_intake
from services.legal_sources import list_public_sources
from services.payment_service import (
    confirm_payment,
    create_payment_intent,
    get_publishable_key,
)
from services.project_service import (
    build_project_response,
    get_job,
    get_project_by_token,
    run_research_job,
)
from services.tier_config import TIER_CONFIG, public_tier_summary

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://owl-ai-agency.com,https://hobie1kenobi.github.io,http://localhost:8000,http://127.0.0.1:5500,http://localhost:5500",
).split(",")

app = FastAPI(
    title="OWL Legal Research API",
    description="Multi-agent paralegal system with tier-gated customer workspace",
    version="2.0.0",
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


@app.get("/api/config/stripe")
async def stripe_config():
    key = get_publishable_key()
    return {"publishable_key": key, "configured": bool(key)}


@app.get("/api/tiers")
async def list_tiers():
    return {"tiers": [public_tier_summary(plan) for plan in TIER_CONFIG]}


@app.get("/api/tiers/{plan}")
async def get_tier_detail(plan: str):
    tier = public_tier_summary(plan)
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    return tier


@app.get("/api/sources")
async def get_sources():
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
    result = await orchestrator.run_demo("carpenter_v_us")
    return result


@app.get("/api/demo/run")
async def run_demo_get():
    return await run_demo()


@app.post("/api/demo-lead", response_model=DemoLeadResponse)
async def create_demo_lead(payload: DemoLeadSubmit):
    return await submit_demo_lead(payload)


@app.post("/api/intake", response_model=IntakeResponse)
async def create_intake(payload: LegalResearchIntake):
    return await submit_intake(payload)


@app.get("/api/intake/{intake_id}")
async def read_intake(intake_id: str):
    record = get_intake(intake_id)
    if not record:
        return {"error": "Intake not found", "intake_id": intake_id}
    return {
        "intake_id": record["intake_id"],
        "status": record.get("status", "received"),
        "payment_status": record.get("payment_status"),
        "submitted_at": record["submitted_at"],
        "plan": record["plan"],
        "firm_name": record["firm_name"],
        "project_access_token": record.get("project_access_token"),
    }


@app.post("/api/payment/create-intent")
async def payment_create_intent(payload: PaymentIntentRequest):
    result = await create_payment_intent(payload.intake_id, payload.plan)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@app.post("/api/payment/confirm")
async def payment_confirm(payload: PaymentConfirmRequest):
    result = await confirm_payment(payload.intake_id, payload.payment_intent_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@app.get("/api/workspace/{access_token}")
async def read_workspace(access_token: str):
    project = build_project_response(access_token)
    if not project:
        raise HTTPException(status_code=404, detail="Workspace not found or access expired")
    return project


@app.post("/api/workspace/{access_token}/research")
async def submit_research(access_token: str, payload: ResearchQueryRequest):
    if not get_project_by_token(access_token):
        raise HTTPException(status_code=404, detail="Workspace not found")
    result = await run_research_job(access_token, payload.model_dump())
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@app.get("/api/workspace/{access_token}/jobs/{job_id}")
async def read_job(access_token: str, job_id: str):
    job = get_job(access_token, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    return job
