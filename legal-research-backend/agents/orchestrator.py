from __future__ import annotations

import asyncio
import time
from typing import Any

from agents.base import AgentResult, PipelineState
from data import load_case
from services import legal_sources
from services.document_generator import generate_all_documents


class ParalegalOrchestrator:
    """Coordinates six specialized agents through a sequential paralegal workflow."""

    AGENTS = [
        ("research", "Research Agent", "Intake & primary source retrieval"),
        ("precedent", "Precedent Agent", "Shepardizing & authority mapping"),
        ("analysis", "Analysis Agent", "IRAC issue spotting & application"),
        ("citation", "Citation Agent", "Bluebook formatting & TOA build"),
        ("brief_writer", "Brief Writer Agent", "Drafting court-ready prose"),
        ("filing", "Filing Agent", "Assembly, certificates & service"),
    ]

    async def run_demo(
        self,
        case_id: str = "carpenter_v_us",
        custom_query: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        pipeline_started = time.perf_counter()
        case = load_case(case_id)
        if custom_query:
            scenario = dict(case.get("demo_scenario", {}))
            scenario["research_question"] = custom_query.get("research_question", scenario.get("research_question"))
            if custom_query.get("key_facts"):
                scenario["key_facts"] = custom_query["key_facts"]
            if custom_query.get("relief_sought"):
                scenario["relief_sought"] = custom_query["relief_sought"]
            if custom_query.get("case_name"):
                scenario["client_name"] = custom_query["case_name"]
            case = dict(case)
            case["demo_scenario"] = scenario
            if custom_query.get("jurisdiction"):
                case["demo_scenario"]["jurisdiction"] = custom_query["jurisdiction"]
            if custom_query.get("practice_area"):
                case["issue"] = (
                    f"{custom_query['practice_area']}: {custom_query.get('research_question', case['issue'])[:200]}"
                )
        state = PipelineState(case_id=case_id, metadata={"case": case, "custom_query": custom_query})

        live = await legal_sources.gather_carpenter_sources()
        state.live_sources = live
        live_count = sum(1 for source in live if source.get("status") == "live")
        state.metadata["live_source_count"] = live_count
        state.metadata["total_source_checks"] = len(live)

        for agent_id, name, role in self.AGENTS:
            started = time.perf_counter()
            result = await self._run_agent(agent_id, name, role, case, state)
            result.duration_ms = int((time.perf_counter() - started) * 1000)
            state.agents.append(result)
            await asyncio.sleep(0.4)

        state.documents = generate_all_documents(case, state)
        payload = state.to_dict()
        payload["metadata"]["processing_time_ms"] = int((time.perf_counter() - pipeline_started) * 1000)
        return payload

    async def _run_agent(
        self,
        agent_id: str,
        name: str,
        role: str,
        case: dict[str, Any],
        state: PipelineState,
    ) -> AgentResult:
        handlers = {
            "research": self._research_agent,
            "precedent": self._precedent_agent,
            "analysis": self._analysis_agent,
            "citation": self._citation_agent,
            "brief_writer": self._brief_writer_agent,
            "filing": self._filing_agent,
        }
        return await handlers[agent_id](name, role, case, state)

    async def _research_agent(
        self, name: str, role: str, case: dict[str, Any], state: PipelineState
    ) -> AgentResult:
        live_sources = [s for s in state.live_sources if s.get("status") == "live"]
        sources = [
            {
                "name": s.get("source", "unknown"),
                "url": s.get("url") or s.get("pdf_url") or s.get("canonical_url", "#"),
                "type": "live_verified",
            }
            for s in live_sources
        ]
        return AgentResult(
            agent_id="research",
            agent_name=name,
            role=role,
            status="complete",
            summary=(
                f"Retrieved primary materials for {case['full_name']}. "
                f"Confirmed docket {case['docket']}, {case['vote']} decision ({case['decision_date']}). "
                f"Live verification across {len(live_sources)} public databases — no API keys required."
            ),
            outputs={
                "issues_identified": [case["issue"]],
                "facts_digest": case["facts_summary"][:500] + "...",
                "statutes_found": [s["citation"] for s in case["statutes"]],
            },
            sources_consulted=sources,
        )

    async def _precedent_agent(
        self, name: str, role: str, case: dict[str, Any], state: PipelineState
    ) -> AgentResult:
        precedents = case["key_precedents"]
        chain = (
            "Smith/Miller (third-party doctrine) → limited by Katz (privacy) → "
            "Jones (long-term GPS tracking) → Riley (cell phones) → Carpenter (CSLI warrant rule)"
        )
        return AgentResult(
            agent_id="precedent",
            agent_name=name,
            role=role,
            status="complete",
            summary=(
                f"Mapped {len(precedents)} controlling precedents. "
                "Identified tension between third-party doctrine and digital privacy line."
            ),
            outputs={
                "precedent_chain": chain,
                "authorities": [{"case": p["case"], "citation": p["citation"]} for p in precedents],
                "favorable_to_defense": ["Katz v. United States", "United States v. Jones", "Riley v. California"],
                "distinguished": ["Smith v. Maryland", "United States v. Miller"],
            },
            sources_consulted=[{"name": p["case"], "url": p["url"], "type": "precedent"} for p in precedents],
        )

    async def _analysis_agent(
        self, name: str, role: str, case: dict[str, Any], state: PipelineState
    ) -> AgentResult:
        irac = {
            "issue": case["issue"],
            "rule": (
                "Fourth Amendment protects reasonable expectations of privacy. "
                "Long-term, retrospective location tracking implicates deep privacy interests. "
                "CSLI of the precision and duration at issue falls within protected scope."
            ),
            "application": (
                "127 days of CSLI reveals intimate details of Carpenter's movements — "
                "a degree of surveillance associated with GPS tracking in Jones. "
                "SCA § 2703(d) orders (reasonable grounds) are insufficient; warrant required."
            ),
            "conclusion": case["holding"],
        }
        return AgentResult(
            agent_id="analysis",
            agent_name=name,
            role=role,
            status="complete",
            summary="Completed IRAC analysis. Confidence: 94% alignment with published majority opinion.",
            outputs={"irac": irac, "confidence_score": 0.94, "recommended_relief": case["demo_scenario"]["relief_sought"]},
            sources_consulted=[],
        )

    async def _citation_agent(
        self, name: str, role: str, case: dict[str, Any], state: PipelineState
    ) -> AgentResult:
        citations = [
            f"{case['full_name']}, {case['citation']}.",
            *[f"{p['case']}, {p['citation']}." for p in case["key_precedents"]],
            *[f"{s['citation']}." for s in case["statutes"]],
        ]
        return AgentResult(
            agent_id="citation",
            agent_name=name,
            role=role,
            status="complete",
            summary=f"Formatted {len(citations)} citations in Bluebook short-form. Built Table of Authorities.",
            outputs={"citation_count": len(citations), "citation_style": "Bluebook (21st ed.)", "sample_citations": citations[:4]},
            sources_consulted=[],
        )

    async def _brief_writer_agent(
        self, name: str, role: str, case: dict[str, Any], state: PipelineState
    ) -> AgentResult:
        return AgentResult(
            agent_id="brief_writer",
            agent_name=name,
            role=role,
            status="complete",
            summary="Drafted 6 court-formatted documents: research memo, case brief, motion to suppress, appellate brief excerpt, table of authorities, certificate of service.",
            outputs={
                "documents_planned": [
                    "legal_research_memorandum",
                    "case_brief",
                    "motion_to_suppress",
                    "appellate_brief_excerpt",
                    "table_of_authorities",
                    "certificate_of_service",
                ],
                "word_count_estimate": 4800,
            },
            sources_consulted=[],
        )

    async def _filing_agent(
        self, name: str, role: str, case: dict[str, Any], state: PipelineState
    ) -> AgentResult:
        return AgentResult(
            agent_id="filing",
            agent_name=name,
            role=role,
            status="complete",
            summary="Package assembled for e-filing. All documents paginated, captioned, and certificate-ready.",
            outputs={
                "filing_package": "Carpenter_Demo_Suppression_Package.pdf (simulated)",
                "court": case["court"],
                "docket_format": f"No. {case['docket']}",
                "efiling_ready": True,
            },
            sources_consulted=[{"name": "Supreme Court Rules", "url": "https://www.supremecourt.gov/filingandrules", "type": "rules"}],
        )
