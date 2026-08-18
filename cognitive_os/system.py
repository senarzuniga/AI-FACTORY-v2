"""Composition root for AI-FACTORY Cognitive Operating System services."""

from __future__ import annotations

from pathlib import Path

from cognitive_os.autonomous import AutonomousExecutionFramework
from cognitive_os.continuous_improvement import ContinuousImprovementRepository
from cognitive_os.ecosystem_discovery import EcosystemDiscovery
from cognitive_os.governance import Governance
from cognitive_os.industrial_intelligence import bootstrap_industrial_intelligence
from cognitive_os.knowledge_core import KnowledgeCoreAPIs
from cognitive_os.memory_core import EnterpriseMemoryCore
from cognitive_os.mission_core import MissionManagerCore
from cognitive_os.mission_model_selection import MissionModelSelector
from cognitive_os.registries import AICoordinator, AgentRegistry, CapabilityGraph, KnowledgeRegistry, MissionGraph, MissionRegistry, PlatformRegistry, RepositoryRegistry
from cognitive_os.runtimes import EvidenceRuntime, HypothesisEngine, ScoringEngine, TruthRuntime, ValidationEngine


class CognitiveOperatingSystem:
    def __init__(self, memory_file: str | None = None) -> None:
        self.coordinator = AICoordinator()
        self.agent_registry = AgentRegistry()
        self.platform_registry = PlatformRegistry()
        self.capability_graph = CapabilityGraph()
        self.repository_registry = RepositoryRegistry()
        self.knowledge_registry = KnowledgeRegistry()
        self.mission_graph = MissionGraph()
        self.mission_registry = MissionRegistry()
        self.mission_model_selector = MissionModelSelector()

        persistence = memory_file or str(Path("data") / "cognitive_os_memory.json")
        self.memory_core = EnterpriseMemoryCore(persistence_file=persistence)

        self.evidence_runtime = EvidenceRuntime()
        self.truth_runtime = TruthRuntime(self.evidence_runtime)
        self.hypothesis_engine = HypothesisEngine()
        self.scoring_engine = ScoringEngine()
        self.validation_engine = ValidationEngine()
        self.governance = Governance()

        self.knowledge_core = KnowledgeCoreAPIs(
            memory_core=self.memory_core,
            evidence_runtime=self.evidence_runtime,
            truth_runtime=self.truth_runtime,
        )

        self.mission_core = MissionManagerCore(
            mission_graph=self.mission_graph,
            hypothesis_engine=self.hypothesis_engine,
            scoring_engine=self.scoring_engine,
            validation_engine=self.validation_engine,
            governance=self.governance,
            mission_registry=self.mission_registry,
        )

        self.industrial_intelligence = bootstrap_industrial_intelligence(self)
        self.continuous_improvement = ContinuousImprovementRepository()
        self.continuous_improvement.ensure_repository()

        self.autonomous = AutonomousExecutionFramework(self.mission_core)
        self.ecosystem_discovery = EcosystemDiscovery(self)

    def evaluate_mission_model(self) -> dict:
        result = self.mission_model_selector.select_best()
        self.memory_core.put("mission_model", "selection", result)
        self.memory_core.put("mission_model", "production_ready", result["production_ready"])
        return result

    def mission_model_production_ready(self) -> bool:
        value = self.memory_core.get("mission_model", "production_ready")
        return bool(value)

    def discover_ecosystem(self) -> dict:
        return self.ecosystem_discovery.discover()

    def mission_control_status(self) -> dict:
        missions = self.mission_core.list_missions()
        active = [mission for mission in missions if mission.status.value == "active"]
        blocked = [mission for mission in missions if mission.status.value == "blocked"]
        pending_gates = [
            {"mission_id": mission.id, "gate": gate.__dict__}
            for mission in missions
            for gate in mission.quality_gates
            if gate.mandatory and gate.status != "passed"
        ]
        open_gaps = [
            {"mission_id": mission.id, "gap": gap.__dict__}
            for mission in missions
            for gap in mission.gaps
            if gap.status != "closed"
        ]
        next_actions = sorted(
            [
                {"mission_id": mission.id, **action.__dict__}
                for mission in missions
                for action in mission.next_actions
                if action.status != "completed"
            ],
            key=lambda item: item["priority_score"],
            reverse=True,
        )
        return {
            "active_missions": [mission.id for mission in active],
            "blocked_missions": [mission.id for mission in blocked],
            "pending_quality_gates": pending_gates,
            "knowledge_gaps": open_gaps,
            "next_actions": next_actions,
            "why_working_on_this": (
                next_actions[0]["description"] if next_actions else "No prioritized executable action is registered"
            ),
            "what_will_it_do_next": next_actions[0] if next_actions else None,
            "no_idle": bool(next_actions),
        }

    def export_state(self) -> dict:
        continuous_root = self.continuous_improvement.repository_path()
        return {
            "agents": [a.__dict__ for a in self.agent_registry.list()],
            "platforms": [p.__dict__ for p in self.platform_registry.list()],
            "capabilities": [c.__dict__ for c in self.capability_graph.list_nodes()],
            "repositories": [r.__dict__ for r in self.repository_registry.list()],
            "knowledge_registry": [k.__dict__ for k in self.knowledge_registry.list()],
            "missions": [m.__dict__ for m in self.mission_core.list_missions()],
            "mission_registry": self.mission_registry.snapshot(),
            "platform_registry_contract": self.platform_registry.contract_version(),
            "capability_registry_schema": self.capability_graph.schema_version(),
            "knowledge": self.knowledge_core.export_snapshot(),
            "events": self.coordinator.recent_events(),
            "mission_model": self.memory_core.get("mission_model", "selection"),
            "industrial_intelligence": self.industrial_intelligence.registration_summary(),
            "continuous_improvement": {
                "repository": continuous_root,
            },
            "mission_control": self.mission_control_status(),
        }
