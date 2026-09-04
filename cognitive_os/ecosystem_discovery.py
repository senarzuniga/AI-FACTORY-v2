"""Read-only ecosystem discovery that feeds canonical Cognitive OS registries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cognitive_os.models import AgentProfile, CapabilityNode, EvidenceRecord, KnowledgeNode, MissionGap, MissionNode, PlatformConsumer, QualityGate, RepositoryNode, utc_now_iso


TARGET_REPOSITORIES = {
    "AI_FACTORY": "AI-FACTORY-v2",
    "IS_BACKOFFICE": "IS-BACKOFFICE",
    "ING_DIGHUB": "ingesite.github.io",
    "ADAPTIVE_SALES_ENGINE": "adaptive-sales-engine",
    "DIGITAL_ECOSYSTEM_PLATFORM": "Digital-Ecosystem-Platform",
    "PLANT_SIMULATOR": "Factoty-Simulator",
}
SKIP_DIRS = {".git", ".venv", "node_modules", "logs", "output", "outputs", "reports", "dist", "build", "__pycache__"}


class EcosystemDiscovery:
    def __init__(self, system: Any, workspace_parent: Path | None = None) -> None:
        self._system = system
        self._repo_root = Path(__file__).resolve().parents[1]
        self._workspace_parent = workspace_parent or self._repo_root.parent

    def discover(self) -> dict[str, Any]:
        repositories = [self._inspect_repository(platform_id, name) for platform_id, name in TARGET_REPOSITORIES.items()]
        for repository in repositories:
            self._system.repository_registry.upsert(repository)
            self._system.platform_registry.register(
                PlatformConsumer(
                    id=repository.id,
                    name=repository.id.replace("_", " ").title(),
                    metadata={
                        "repository": repository.path,
                        "status": repository.status,
                        "entrypoints": repository.entrypoints,
                        "apis": repository.apis,
                        "tests": repository.tests,
                    },
                )
            )
            for agent_path in repository.agents:
                agent_id = f"{repository.id}:{agent_path}"
                self._system.agent_registry.register(
                    AgentProfile(
                        id=agent_id,
                        name=Path(agent_path).stem,
                        capabilities=["mission_contributing_execution"],
                        metadata={"repository": repository.id, "path": agent_path},
                    )
                )

        capability_sources = self._load_capability_sources()
        for item in capability_sources:
            capability_id = self._slug(str(item.get("name", "unknown-capability")))
            evidence = [str(value) for value in item.get("evidence", [])]
            verified = [path for path in evidence if (self._repo_root / path).exists()]
            self._system.capability_graph.upsert_node(
                CapabilityNode(
                    id=capability_id,
                    description=str(item.get("name", capability_id)),
                    interfaces=verified,
                )
            )
            self._system.knowledge_registry.upsert(
                KnowledgeNode(
                    id=f"KN-CAP-{capability_id}",
                    topic="capability_discovery",
                    statement=f"Capability {item.get('name')} has {len(verified)} verified evidence artifact(s).",
                    classification="VALIDATED" if verified else "UNKNOWN",
                    source="docs/aeos_review/Capability_Registry.json",
                    evidence=verified,
                    confidence=1.0 if evidence and len(verified) == len(evidence) else (0.65 if verified else 0.0),
                    validation_status="validated" if verified else "requires_validation",
                    metadata={"previous_status": item.get("status"), "evidence_declared": evidence},
                )
            )

        summary = {
            "discovered_at": utc_now_iso(),
            "repositories": len(repositories),
            "available_repositories": sum(item.status == "available" for item in repositories),
            "platforms": len(self._system.platform_registry.list()),
            "capabilities": len(self._system.capability_graph.list_nodes()),
            "agents": len(self._system.agent_registry.list()),
            "knowledge_records": len(self._system.knowledge_registry.list()),
            "missing_repositories": [item.id for item in repositories if item.status != "available"],
        }
        evidence = EvidenceRecord(
            id="evidence-ecosystem-discovery-latest",
            source="cognitive_os.ecosystem_discovery",
            payload=summary,
            mission_id="IMPROVE-AI-FACTORY",
        )
        self._system.evidence_runtime.add(evidence)
        self._upsert_improvement_mission(repositories, evidence.id)
        self._system.memory_core.put("ecosystem", "discovery", summary)
        self._system.coordinator.publish("ecosystem.discovery.completed", summary)
        return summary

    def _inspect_repository(self, platform_id: str, directory_name: str) -> RepositoryNode:
        path = self._workspace_parent / directory_name
        if not path.is_dir():
            return RepositoryNode(id=platform_id, path=str(path), status="missing", known_gaps=["repository_not_available"])

        files = self._bounded_files(path)
        relative = [item.relative_to(path).as_posix() for item in files]
        instructions = [item for item in relative if item in {"AGENTS.md", ".github/copilot-instructions.md", "governance/global_operational_directive.md"}]
        agents = [
            item for item in relative
            if "agent" in Path(item).stem.lower()
            and Path(item).suffix in {".py", ".md"}
            and Path(item).name not in {"AGENTS.md", "copilot-instructions.md"}
        ]
        tests = [item for item in relative if "tests" in Path(item).parts and Path(item).name.startswith("test_")]
        apis = [item for item in relative if "api" in Path(item).parts and Path(item).suffix == ".py"]
        entrypoints = [item for item in relative if Path(item).name.lower() in {"main.py", "app.py", "index.html", "package.json", "launch.ps1"}]
        dependencies = [item for item in relative if Path(item).name in {"requirements.txt", "pyproject.toml", "package.json", "environment.yml"}]
        purpose = self._read_purpose(path)
        gaps = [] if instructions else ["governance_directive_not_detected"]
        return RepositoryNode(
            id=platform_id,
            path=str(path),
            status="available",
            purpose=purpose,
            entrypoints=entrypoints,
            apis=apis,
            agents=agents,
            tests=tests,
            instructions=instructions,
            dependencies=dependencies,
            known_gaps=gaps,
            metadata={"files_indexed": len(relative), "git_repository": (path / ".git").exists()},
        )

    def _bounded_files(self, root: Path, max_files: int = 8_000) -> list[Path]:
        files: list[Path] = []
        pending = [root]
        while pending and len(files) < max_files:
            current = pending.pop()
            try:
                children = list(current.iterdir())
            except OSError:
                continue
            for child in children:
                if child.is_dir() and child.name not in SKIP_DIRS:
                    pending.append(child)
                elif child.is_file() and child.stat().st_size <= 1_500_000:
                    files.append(child)
                    if len(files) >= max_files:
                        break
        return files

    def _read_purpose(self, root: Path) -> str:
        for name in ("README.md", "README.txt"):
            path = root / name
            if path.exists():
                for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    statement = line.strip().lstrip("#").strip()
                    if statement:
                        return statement[:300]
        return "Purpose not documented"

    def _load_capability_sources(self) -> list[dict[str, Any]]:
        path = self._repo_root / "docs" / "aeos_review" / "Capability_Registry.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [item for item in payload.get("capabilities", []) if isinstance(item, dict)]

    def _upsert_improvement_mission(self, repositories: list[RepositoryNode], evidence_id: str) -> None:
        mission_id = "IMPROVE-AI-FACTORY"
        existing = self._system.mission_graph.get(mission_id)
        gaps: list[MissionGap] = []
        for repository in repositories:
            if "governance_directive_not_detected" in repository.known_gaps:
                gaps.append(
                    MissionGap(
                        id=f"G-GOVERNANCE-{repository.id}",
                        statement=f"Audit and safely synchronize governance instructions for {repository.id}",
                        priority=5,
                        required_capability="engineering-governance",
                    )
                )
            if repository.status == "available" and not repository.tests:
                gaps.append(
                    MissionGap(
                        id=f"G-TESTS-{repository.id}",
                        statement=f"Establish executable contract tests for {repository.id}",
                        priority=4,
                        required_capability="quality-assurance",
                    )
                )
        gaps.extend(
            [
                MissionGap(
                    id="G-CROSS-REPOSITORY-CONTRACT",
                    statement="Validate mission submission and evidence return across connected repositories",
                    priority=5,
                    required_capability="workflow-orchestration",
                ),
                MissionGap(
                    id="G-INSTRUCTION-AUDIT",
                    statement="Classify existing ecosystem instructions as compatible, complementary, redundant, conflicting, obsolete or unknown",
                    priority=5,
                    required_capability="engineering-governance",
                ),
            ]
        )
        closed_by_id = {gap.id: gap for gap in existing.gaps if gap.status == "closed"} if existing else {}
        gaps = [closed_by_id.get(gap.id, gap) for gap in gaps]
        gates = [
            QualityGate(
                id="Q-DISCOVERY",
                description="All governed repositories discovered",
                status="passed" if all(item.status == "available" for item in repositories) else "pending",
                evidence_ids=[evidence_id],
            ),
            QualityGate(id="Q-INSTRUCTIONS", description="Instruction audit and conflict map validated"),
            QualityGate(id="Q-CONTRACT", description="Cross-repository mission contract test passes"),
            QualityGate(id="Q-E2E", description="End-to-end mission, evidence, learning and continuation test passes"),
            QualityGate(id="Q-SECURITY", description="Security and governed autonomy tests pass"),
            QualityGate(id="Q-RECOVERY", description="Recovery and data-integrity tests pass"),
        ]
        if existing:
            status_by_id = {gate.id: gate for gate in existing.quality_gates if gate.status == "passed"}
            gates = [status_by_id.get(gate.id, gate) for gate in gates]
            mission = existing
            mission.gaps = gaps
            mission.quality_gates = gates
            if evidence_id not in mission.evidence_ids:
                mission.evidence_ids.append(evidence_id)
        else:
            mission = MissionNode(
                id=mission_id,
                title="Improve AI_FACTORY",
                objective="Continuously improve governed ecosystem orchestration until mission quality gates pass.",
                gaps=gaps,
                quality_gates=gates,
                evidence_ids=[evidence_id],
                capabilities=["mission-management", "engineering-governance", "workflow-orchestration"],
                tags=["permanent", "self-improvement", "ecosystem"],
            )
        self._system.mission_core.upsert_mission(mission)
        self._system.mission_core.refresh_readiness(mission_id)

    @staticmethod
    def _slug(value: str) -> str:
        return "-".join(value.lower().replace("/", " ").split())