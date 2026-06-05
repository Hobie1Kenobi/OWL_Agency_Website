from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AgentResult:
    agent_id: str
    agent_name: str
    role: str
    status: str
    summary: str
    outputs: dict[str, Any] = field(default_factory=dict)
    sources_consulted: list[dict[str, Any]] = field(default_factory=list)
    duration_ms: int = 0


@dataclass
class PipelineState:
    case_id: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agents: list[AgentResult] = field(default_factory=list)
    documents: dict[str, str] = field(default_factory=dict)
    live_sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "started_at": self.started_at,
            "agents": [
                {
                    "agent_id": a.agent_id,
                    "agent_name": a.agent_name,
                    "role": a.role,
                    "status": a.status,
                    "summary": a.summary,
                    "outputs": a.outputs,
                    "sources_consulted": a.sources_consulted,
                    "duration_ms": a.duration_ms,
                }
                for a in self.agents
            ],
            "documents": self.documents,
            "live_sources": self.live_sources,
            "metadata": self.metadata,
        }
