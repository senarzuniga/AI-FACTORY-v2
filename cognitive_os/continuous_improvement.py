"""Continuous Mission Optimization Engine governance repository manager."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ObjectiveSpec:
    objective_id: str
    title: str
    priority: str
    dependencies: list[str]
    expected_value: str
    acceptance_criteria: list[str]
    kpis: list[str]
    owner: str
    target_architecture: str


class ContinuousImprovementRepository:
    """Maintains Architecture/ContinuousImprovement as single source of truth."""

    def __init__(self, root_dir: str | None = None) -> None:
        self._root = Path(root_dir or "Architecture/ContinuousImprovement")
        self._objectives_file = self._root / "01_OBJECTIVES.md"
        self._current_file = self._root / "02_CURRENT_STATE.md"
        self._gaps_file = self._root / "03_GAP_ANALYSIS.md"
        self._backlog_file = self._root / "04_EXECUTION_BACKLOG.md"
        self._history_file = self._root / "05_PROGRESS_HISTORY.md"

    def ensure_repository(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        if not self._objectives_file.exists():
            self._objectives_file.write_text(self._default_objectives_markdown(), encoding="utf-8")
        if not self._history_file.exists():
            self._history_file.write_text("# Progress History\n\n", encoding="utf-8")

    def repository_path(self) -> str:
        return str(self._root)

    def refresh(self, state: dict[str, Any], mission_event: dict[str, Any]) -> dict[str, Any]:
        self.ensure_repository()
        objectives = self._objective_specs()
        current = self._build_current_state(state)
        gaps = self._build_gap_analysis(objectives, current)
        backlog = self._build_execution_backlog(gaps)

        self._current_file.write_text(current, encoding="utf-8")
        self._gaps_file.write_text(gaps, encoding="utf-8")
        self._backlog_file.write_text(backlog, encoding="utf-8")
        self._append_history(mission_event, state, gaps)

        unresolved = self._count_unresolved_gaps(gaps)
        return {
            "repository": str(self._root),
            "updated_at": _now(),
            "unresolved_gaps": unresolved,
            "idle_permitted": unresolved == 0,
        }

    def _objective_specs(self) -> list[ObjectiveSpec]:
        return [
            ObjectiveSpec(
                objective_id="OBJ-M013-001",
                title="Universal CAD ingestion",
                priority="critical",
                dependencies=[],
                expected_value="CAD-independent layout ingestion across enterprise",
                acceptance_criteria=["Pluggable providers active", "DWG failover active", "Intermediate model mandatory"],
                kpis=["supported_formats>=8", "provider_failover=true"],
                owner="AI Coordinator",
                target_architecture="cognitive_os.layout_import_framework",
            ),
            ObjectiveSpec(
                objective_id="OBJ-M013-002",
                title="Persistent layout versioning",
                priority="critical",
                dependencies=["OBJ-M013-001"],
                expected_value="Reproducible snapshots and scenario branches",
                acceptance_criteria=["snapshot persistence", "diff and rollback"],
                kpis=["revision_history=true", "rollback=true"],
                owner="Mission Manager",
                target_architecture="cognitive_os.layout_versioning",
            ),
            ObjectiveSpec(
                objective_id="OBJ-M013-003",
                title="Automatic knowledge and evidence synchronization",
                priority="high",
                dependencies=["OBJ-M013-001"],
                expected_value="No engineering knowledge loss",
                acceptance_criteria=["object evidence generated", "knowledge synchronized"],
                kpis=["evidence_per_object>=1", "sync_cycle_success>=0.95"],
                owner="Knowledge Core",
                target_architecture="cognitive_os.sdk + knowledge_core",
            ),
            ObjectiveSpec(
                objective_id="OBJ-CMOE-001",
                title="Continuous Mission Optimization Engine",
                priority="critical",
                dependencies=["OBJ-M013-001", "OBJ-M013-002", "OBJ-M013-003"],
                expected_value="No idle state while executable work exists",
                acceptance_criteria=["governance docs auto-updated", "gap-driven backlog auto-generated"],
                kpis=["idle_state=false", "backlog_refresh_per_mission=1"],
                owner="AI Coordinator",
                target_architecture="Architecture/ContinuousImprovement",
            ),
        ]

    def _default_objectives_markdown(self) -> str:
        lines = [
            "# Objectives",
            "",
            "Automatically maintained objective baseline for CMOE.",
            "",
        ]
        for spec in self._objective_specs():
            lines.extend(
                [
                    f"## {spec.objective_id} — {spec.title}",
                    f"- Priority: {spec.priority}",
                    f"- Dependencies: {', '.join(spec.dependencies) if spec.dependencies else 'None'}",
                    f"- Expected Value: {spec.expected_value}",
                    f"- Acceptance Criteria: {'; '.join(spec.acceptance_criteria)}",
                    f"- KPIs: {'; '.join(spec.kpis)}",
                    "- Completion Percentage: 0%",
                    "- Required Evidence: runtime evidence + tests + docs",
                    f"- Owner: {spec.owner}",
                    f"- Target Architecture: {spec.target_architecture}",
                    "",
                ]
            )
        return "\n".join(lines)

    def _build_current_state(self, state: dict[str, Any]) -> str:
        mission_registry = state.get("mission_registry", {})
        missions = mission_registry.get("missions", [])
        capabilities = state.get("capabilities", [])
        platforms = state.get("platforms", [])
        truth = state.get("knowledge", {}).get("truth", [])
        evidence = state.get("knowledge", {}).get("evidence", [])

        status = "Working" if capabilities and platforms else "Partially Working"
        lines = [
            "# Current State",
            "",
            f"Generated At: {_now()}",
            "",
            "## Repository Classification",
            f"- Cognitive OS Runtime: {status}",
            f"- Mission Manager: {'Working' if missions else 'Partially Working'}",
            f"- Capability Registry: {'Working' if capabilities else 'Unknown'}",
            f"- Platform Registry: {'Working' if platforms else 'Unknown'}",
            f"- Evidence Runtime: {'Working' if evidence else 'Partially Working'}",
            f"- Knowledge Graph Runtime: {'Working' if truth else 'Partially Working'}",
            "",
            "## Coverage",
            f"- Missions: {len(missions)}",
            f"- Capabilities: {len(capabilities)}",
            f"- Platforms: {len(platforms)}",
            f"- Evidence Records: {len(evidence)}",
            f"- Truth Assertions: {len(truth)}",
            "",
            "## Architecture Health",
            f"- Readiness: {'production-candidate' if len(capabilities) >= 10 else 'in-progress'}",
            f"- Technical Debt: {'medium' if len(capabilities) < 20 else 'low'}",
            f"- Evidence Integrity: {'good' if evidence else 'partial'}",
        ]
        return "\n".join(lines) + "\n"

    def _build_gap_analysis(self, objectives: list[ObjectiveSpec], current_markdown: str) -> str:
        current_lower = current_markdown.lower()
        gaps: list[dict[str, Any]] = []
        for item in objectives:
            done = item.target_architecture.lower() in current_lower
            if not done:
                gaps.append(
                    {
                        "objective_id": item.objective_id,
                        "gap": item.title,
                        "priority": item.priority,
                        "business_impact": "high" if item.priority == "critical" else "medium",
                        "industrial_impact": "high",
                        "architecture_impact": "high",
                        "dependencies": item.dependencies,
                        "estimated_effort": "M",
                        "risk": "medium",
                        "expected_score_improvement": 0.08 if item.priority == "critical" else 0.05,
                        "recommended_mission": f"MISSION-{item.objective_id}",
                    }
                )

        lines = [
            "# Gap Analysis",
            "",
            f"Generated At: {_now()}",
            "",
            "## Gaps",
        ]
        if not gaps:
            lines.append("- No unresolved gaps detected.")
        for gap in gaps:
            lines.extend(
                [
                    f"### {gap['objective_id']} — {gap['gap']}",
                    f"- Priority: {gap['priority']}",
                    f"- Business Impact: {gap['business_impact']}",
                    f"- Industrial Impact: {gap['industrial_impact']}",
                    f"- Architecture Impact: {gap['architecture_impact']}",
                    f"- Dependencies: {', '.join(gap['dependencies']) if gap['dependencies'] else 'None'}",
                    f"- Estimated Effort: {gap['estimated_effort']}",
                    f"- Risk: {gap['risk']}",
                    f"- Expected Score Improvement: {gap['expected_score_improvement']}",
                    f"- Recommended Mission: {gap['recommended_mission']}",
                    "",
                ]
            )
        return "\n".join(lines)

    def _build_execution_backlog(self, gaps_markdown: str) -> str:
        missions: list[dict[str, Any]] = []
        for line in gaps_markdown.splitlines():
            if line.startswith("### "):
                header = line.removeprefix("### ").strip()
                if " — " in header:
                    objective_id, title = header.split(" — ", 1)
                else:
                    objective_id, title = header, header
                missions.append(
                    {
                        "mission_id": f"AUTO-{objective_id}",
                        "title": title,
                        "priority": "critical",
                        "dependencies": "auto",
                        "business_value": 0.8,
                        "industrial_value": 0.85,
                        "architecture_value": 0.9,
                        "expected_roi": 0.7,
                        "expected_oee_impact": 0.08,
                        "confidence": 0.72,
                        "risk": 0.35,
                        "estimated_duration": "3d",
                        "required_agents": "AI Coordinator, Mission Manager",
                        "executive_score": 0.79,
                        "ahde_score": 0.81,
                    }
                )

        lines = [
            "# Execution Backlog",
            "",
            f"Generated At: {_now()}",
            "",
            "| Mission ID | Priority | Business Value | Industrial Value | Architecture Value | ROI | OEE Impact | Confidence | Risk | Duration | Executive Score | AHDE Score |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|",
        ]
        if not missions:
            lines.append("| IDLE | low | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0d | 0.0 | 0.0 |")
        for item in missions:
            lines.append(
                f"| {item['mission_id']} | {item['priority']} | {item['business_value']} | {item['industrial_value']} | {item['architecture_value']} | {item['expected_roi']} | {item['expected_oee_impact']} | {item['confidence']} | {item['risk']} | {item['estimated_duration']} | {item['executive_score']} | {item['ahde_score']} |"
            )
        return "\n".join(lines) + "\n"

    def _append_history(self, mission_event: dict[str, Any], state: dict[str, Any], gaps_markdown: str) -> None:
        unresolved = self._count_unresolved_gaps(gaps_markdown)
        entry = {
            "timestamp": _now(),
            "mission": mission_event.get("mission_id", "unknown"),
            "event": mission_event.get("event", "refresh"),
            "duration_seconds": mission_event.get("duration_seconds", 0),
            "agents": mission_event.get("agents", []),
            "evidence_count": len(state.get("knowledge", {}).get("evidence", [])),
            "architecture_changes": mission_event.get("architecture_changes", []),
            "knowledge_generated": mission_event.get("knowledge_generated", []),
            "lessons_learned": mission_event.get("lessons_learned", []),
            "executive_score_before": mission_event.get("executive_score_before", 0.0),
            "executive_score_after": mission_event.get("executive_score_after", 0.0),
            "objectives_completed": mission_event.get("objectives_completed", []),
            "remaining_gaps": unresolved,
            "generated_reports": [
                str(self._current_file),
                str(self._gaps_file),
                str(self._backlog_file),
            ],
        }
        with self._history_file.open("a", encoding="utf-8") as handle:
            handle.write(f"- {json.dumps(entry, ensure_ascii=True)}\n")

    def _count_unresolved_gaps(self, gaps_markdown: str) -> int:
        return sum(1 for line in gaps_markdown.splitlines() if line.startswith("### "))
