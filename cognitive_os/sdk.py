"""SDK facade for consumers such as IS_BACKOFFICE and ING_DIGHUB."""

from __future__ import annotations

from typing import Any

from cognitive_os.models import AgentProfile, CapabilityNode, EvidenceRecord, Hypothesis, MissionNode, PlatformConsumer, TruthAssertion
from cognitive_os.system import CognitiveOperatingSystem


class CognitiveOSSDK:
    def __init__(self, system: CognitiveOperatingSystem) -> None:
        self._system = system

    def register_agent(self, payload: dict) -> None:
        self._system.agent_registry.register(AgentProfile(**payload))

    def register_platform(self, payload: dict) -> None:
        self._system.platform_registry.register(PlatformConsumer(**payload))

    def upsert_capability(self, payload: dict) -> None:
        self._system.capability_graph.upsert_node(CapabilityNode(**payload))

    def upsert_mission(self, payload: dict) -> None:
        self._system.mission_core.upsert_mission(MissionNode(**payload))

    def submit_hypothesis(self, payload: dict) -> None:
        self._system.hypothesis_engine.submit(Hypothesis(**payload))

    def ingest_evidence(self, payload: dict) -> None:
        self._system.knowledge_core.ingest_evidence(EvidenceRecord(**payload))

    def assert_truth(self, payload: dict) -> dict:
        result = self._system.knowledge_core.assert_truth(TruthAssertion(**payload))
        return result.__dict__

    def run_autonomous(self, max_cycles: int = 100) -> dict:
        if not self._system.mission_model_production_ready():
            return {
                "status": "blocked",
                "reason": "Mission Model is not Production Ready",
                "required_action": "evaluate_and_select_canonical_mission_model",
            }
        result = self._system.autonomous.run_until_stable(max_cycles=max_cycles)
        refresh = self._system.continuous_improvement.refresh(
            state=self.export_state(),
            mission_event={
                "mission_id": "AUTONOMOUS",
                "event": "autonomous_run",
                "duration_seconds": 0,
                "agents": ["Mission Manager", "AI Coordinator"],
                "executive_score_before": 0.0,
                "executive_score_after": 0.0,
            },
        )
        result["continuous_improvement"] = refresh
        return result

    def evaluate_mission_model(self) -> dict:
        return self._system.evaluate_mission_model()

    def mission_model_production_ready(self) -> bool:
        return self._system.mission_model_production_ready()

    def industrial_intelligence_status(self) -> dict:
        return self._system.industrial_intelligence.health()

    def industrial_intelligence_components(self) -> list[dict]:
        return self._system.industrial_intelligence.list_components()

    def industrial_intelligence_component(self, component_id: str) -> dict:
        return self._system.industrial_intelligence.component(component_id)

    def industrial_intelligence_execute(self, component_id: str, payload: dict) -> dict:
        result = self._system.industrial_intelligence.execute_component(component_id, payload)
        ts = str(result.get("timestamp", "")).replace(":", "-").replace(".", "-")
        evidence_payload = {
            "id": f"evidence-{component_id}-{ts}",
            "source": component_id,
            "payload": result,
            "mission_id": "M010",
        }
        self.ingest_evidence(evidence_payload)

        self._sync_layout_knowledge(result)
        self._ingest_object_evidence(result)
        refresh = self._system.continuous_improvement.refresh(
            state=self.export_state(),
            mission_event={
                "mission_id": str(payload.get("mission_id") or "M013"),
                "event": f"component_execute:{component_id}",
                "duration_seconds": 0,
                "agents": ["IndustrialLayoutInterpreter", "CognitiveOSSDK"],
                "architecture_changes": ["layout_import", "knowledge_sync", "continuous_repo_refresh"],
                "knowledge_generated": ["factory_graph", "knowledge_graph", "digital_twin"],
                "lessons_learned": ["provider failover trace persisted"],
            },
        )
        result["continuous_improvement"] = refresh
        return result

    def industrial_intelligence_ahde(self, mission_id: str, uncertainty: str, context: dict) -> dict:
        decision = self._system.industrial_intelligence.ahde_decide(
            mission_id=mission_id,
            uncertainty=uncertainty,
            context=context,
        )
        self._system.memory_core.put("industrial_intelligence", "last_ahde_decision", decision)
        return decision

    def export_state(self) -> dict:
        return self._system.export_state()

    def _sync_layout_knowledge(self, result: dict[str, Any]) -> None:
        factory_graph = result.get("factory_graph") if isinstance(result.get("factory_graph"), dict) else {}
        knowledge_graph = result.get("knowledge_graph") if isinstance(result.get("knowledge_graph"), dict) else {}
        digital_twin = result.get("digital_twin") if isinstance(result.get("digital_twin"), dict) else {}
        simulation = result.get("simulation") if isinstance(result.get("simulation"), dict) else {}
        engineering = result.get("engineering_analysis") if isinstance(result.get("engineering_analysis"), dict) else {}

        if factory_graph:
            self._system.memory_core.put("factory_graph", "latest", factory_graph)
        if knowledge_graph:
            self._system.memory_core.put("knowledge_graph", "latest", knowledge_graph)
        if digital_twin:
            self._system.memory_core.put("digital_twin", "latest", digital_twin)
        if simulation:
            self._system.memory_core.put("simulation", "latest", simulation)
        if engineering:
            self._system.memory_core.put("engineering_analysis", "latest", engineering)

    def _ingest_object_evidence(self, result: dict[str, Any]) -> None:
        object_evidence = result.get("object_evidence")
        if not isinstance(object_evidence, list):
            return
        for item in object_evidence:
            if isinstance(item, dict):
                self.ingest_evidence(item)
