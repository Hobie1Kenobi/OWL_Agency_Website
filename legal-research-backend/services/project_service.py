"""Customer project workspace — tier-gated paralegal access."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.orchestrator import ParalegalOrchestrator
from services.intake_service import get_intake
from services.tier_config import get_tier, public_tier_summary

PROJECTS_DIR = Path(__file__).resolve().parent.parent / "data" / "projects"
orchestrator = ParalegalOrchestrator()

ONBOARDING_STEPS = [
    {
        "id": "welcome",
        "title": "Review your package",
        "description": "See which documents, case limits, and turnaround apply to your tier.",
    },
    {
        "id": "question",
        "title": "Frame your research question",
        "description": "Use the guided form — issue, jurisdiction, facts, and relief sought.",
    },
    {
        "id": "run",
        "title": "Run the paralegal pipeline",
        "description": "Six AI agents research, analyze, cite, draft, and assemble filings.",
    },
    {
        "id": "deliver",
        "title": "Download deliverables",
        "description": "Export documents and CSV reports. Attorney review recommended.",
    },
]


def _ensure_storage() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def _project_path(access_token: str) -> Path:
    return PROJECTS_DIR / f"{access_token}.json"


def _save_project(project: dict[str, Any]) -> None:
    _ensure_storage()
    _project_path(project["access_token"]).write_text(
        json.dumps(project, indent=2), encoding="utf-8"
    )


def _load_project(access_token: str) -> dict[str, Any] | None:
    path = _project_path(access_token)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def activate_project_for_intake(
    intake_id: str,
    plan: str,
    payment_intent_id: str,
) -> dict[str, Any]:
    intake = get_intake(intake_id)
    if not intake:
        raise ValueError("Intake not found")

    tier = get_tier(plan)
    if not tier:
        raise ValueError("Invalid plan")

    access_token = uuid.uuid4().hex
    api_key = f"owl_{uuid.uuid4().hex}" if tier["api_access"] else None
    now = datetime.now(timezone.utc).isoformat()

    project = {
        "access_token": access_token,
        "intake_id": intake_id,
        "plan": plan,
        "firm_name": intake["firm_name"],
        "contact_name": intake["full_name"],
        "contact_email": intake["email"],
        "payment_intent_id": payment_intent_id,
        "status": "active",
        "activated_at": now,
        "cases_used": 0,
        "research_jobs": [],
        "api_key": api_key,
        "initial_research_question": intake.get("research_question"),
        "jurisdiction": intake.get("jurisdiction"),
        "practice_area": intake.get("practice_area"),
    }
    _save_project(project)
    return project


def get_project_by_token(access_token: str) -> dict[str, Any] | None:
    return _load_project(access_token)


def _filter_documents(documents: dict[str, str], allowed: list[str]) -> dict[str, str]:
    return {key: documents[key] for key in allowed if key in documents}


def _build_csv_export(job: dict[str, Any], tier: dict[str, Any]) -> str:
    """Generate tier-appropriate CSV summary."""
    lines = ["field,value"]
    lines.append(f"case_name,{_csv_escape(job.get('case_name', ''))}")
    lines.append(f"jurisdiction,{_csv_escape(job.get('jurisdiction', ''))}")
    lines.append(f"practice_area,{_csv_escape(job.get('practice_area', ''))}")
    lines.append(f"research_question,{_csv_escape(job.get('research_question', ''))}")
    lines.append(f"plan,{_csv_escape(tier['name'])}")
    lines.append(f"completed_at,{_csv_escape(job.get('completed_at', ''))}")

    if tier["excel_export"] in ("interactive", "advanced"):
        lines.append("precedent,principle")
        for p in job.get("precedents", []):
            lines.append(f"{_csv_escape(p.get('case', ''))},{_csv_escape(p.get('principle', ''))}")

    if tier["excel_export"] == "advanced":
        lines.append("metric,value")
        lines.append(f"agents_deployed,{len(job.get('agents', []))}")
        lines.append(f"documents_generated,{len(job.get('documents', {}))}")
        lines.append(f"live_sources,{job.get('live_source_count', 0)}")
        lines.append(f"processing_seconds,{job.get('processing_time_ms', 0) / 1000}")

    return "\n".join(lines)


def _csv_escape(value: str) -> str:
    text = str(value).replace('"', '""')
    if "," in text or '"' in text or "\n" in text:
        return f'"{text}"'
    return text


async def run_research_job(access_token: str, query: dict[str, Any]) -> dict[str, Any]:
    project = _load_project(access_token)
    if not project:
        return {"error": "Project not found"}

    tier = get_tier(project["plan"])
    if not tier:
        return {"error": "Invalid project tier"}

    if project["cases_used"] >= tier["case_limit"]:
        return {
            "error": "Case limit reached",
            "detail": f"Your {tier['name']} includes {tier['case_limit']} research runs.",
            "cases_used": project["cases_used"],
            "case_limit": tier["case_limit"],
        }

    pipeline = await orchestrator.run_demo("carpenter_v_us", custom_query=query)
    all_docs = pipeline.get("documents", {})
    filtered_docs = _filter_documents(all_docs, tier["documents"])

    job_id = f"JOB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    job = {
        "job_id": job_id,
        "case_name": query["case_name"],
        "jurisdiction": query["jurisdiction"],
        "practice_area": query["practice_area"],
        "research_question": query["research_question"],
        "key_facts": query.get("key_facts"),
        "relief_sought": query.get("relief_sought"),
        "status": "complete",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "agents": pipeline.get("agents", []),
        "documents": filtered_docs,
        "document_labels": tier["document_labels"],
        "live_sources": pipeline.get("live_sources", []),
        "live_source_count": pipeline.get("metadata", {}).get("live_source_count", 0),
        "processing_time_ms": pipeline.get("metadata", {}).get("processing_time_ms", 0),
        "precedents": pipeline.get("metadata", {}).get("case", {}).get("key_precedents", []),
        "csv_export": _build_csv_export(
            {
                **query,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "agents": pipeline.get("agents", []),
                "documents": filtered_docs,
                "live_source_count": pipeline.get("metadata", {}).get("live_source_count", 0),
                "processing_time_ms": pipeline.get("metadata", {}).get("processing_time_ms", 0),
                "precedents": pipeline.get("metadata", {}).get("case", {}).get("key_precedents", []),
            },
            tier,
        ),
        "tier_documents_available": tier["documents"],
        "excel_export_level": tier["excel_export"],
    }

    project["cases_used"] += 1
    project["research_jobs"].insert(0, {
        "job_id": job_id,
        "case_name": query["case_name"],
        "status": "complete",
        "created_at": job["created_at"],
        "document_count": len(filtered_docs),
    })
    _save_project(project)
    job_path = PROJECTS_DIR / f"{access_token}_{job_id}.json"
    job_path.write_text(json.dumps(job, indent=2), encoding="utf-8")

    return {
        "success": True,
        "job": job,
        "cases_used": project["cases_used"],
        "cases_remaining": max(0, tier["case_limit"] - project["cases_used"]),
    }


def get_job(access_token: str, job_id: str) -> dict[str, Any] | None:
    project = _load_project(access_token)
    if not project:
        return None

    for job in project.get("research_jobs", []):
        if job["job_id"] == job_id:
            job_path = PROJECTS_DIR / f"{access_token}_{job_id}.json"
            if job_path.exists():
                return json.loads(job_path.read_text(encoding="utf-8"))
    return None


def build_project_response(access_token: str, base_url: str = "") -> dict[str, Any] | None:
    project = _load_project(access_token)
    if not project:
        return None

    tier = get_tier(project["plan"])
    if not tier:
        return None

    steps = []
    for i, step in enumerate(ONBOARDING_STEPS):
        done = False
        if step["id"] == "welcome":
            done = True
        elif step["id"] == "question" and project.get("initial_research_question"):
            done = True
        elif step["id"] == "run" and project.get("cases_used", 0) > 0:
            done = True
        elif step["id"] == "deliver" and project.get("cases_used", 0) > 0:
            done = True
        steps.append({**step, "complete": done, "step_number": i + 1})

    workspace_path = f"/legal-research-workspace.html?token={access_token}"
    return {
        "access_token": access_token,
        "intake_id": project["intake_id"],
        "plan": project["plan"],
        "tier": public_tier_summary(project["plan"]),
        "firm_name": project["firm_name"],
        "contact_name": project["contact_name"],
        "contact_email": project["contact_email"],
        "status": project["status"],
        "cases_used": project["cases_used"],
        "cases_remaining": max(0, tier["case_limit"] - project["cases_used"]),
        "case_limit": tier["case_limit"],
        "research_jobs": project.get("research_jobs", []),
        "onboarding_steps": steps,
        "api_key": project.get("api_key") if tier["api_access"] else None,
        "workspace_url": workspace_path,
        "initial_research_question": project.get("initial_research_question"),
        "jurisdiction": project.get("jurisdiction"),
        "practice_area": project.get("practice_area"),
    }
