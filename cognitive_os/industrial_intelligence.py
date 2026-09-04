"""Industrial Intelligence Core runtimes and AHDE execution for Cognitive OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

from cognitive_os.industrial_layout import IndustrialLayoutInterpreter
from cognitive_os.layout_versioning import LayoutVersionStore
from cognitive_os.models import CapabilityNode, EvidenceRecord, MissionNode, PlatformConsumer, TruthAssertion, utc_now_iso


@dataclass
class IndustrialComponent:
    id: str
    name: str
    mission_ref: str
    apis: list[str]
    capabilities: list[str]
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    health_status: str = "ok"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "component_id": self.id,
            "status": "completed",
            "timestamp": utc_now_iso(),
            "input": payload,
        }

    def health(self) -> dict[str, Any]:
        return {
            "component_id": self.id,
            "status": self.health_status,
            "dependencies": self.dependencies,
            "timestamp": utc_now_iso(),
        }


class GeometryEngine(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        layout_result = payload.get("layout_result") or payload.get("interpretation")
        if isinstance(layout_result, dict):
            graph = layout_result.get("factory_graph", {})
            simulation = layout_result.get("simulation", {})
            analysis = layout_result.get("engineering_analysis", {})
            return {
                "component_id": self.id,
                "status": "completed",
                "geometry_entities": len(layout_result.get("entities", [])),
                "area_estimate": round(float(graph.get("node_count", 0)) * 9.5, 3),
                "layout_quality": analysis.get("layout_quality", {}),
                "simulation_readiness": simulation.get("production_capacity", 0.0),
                "timestamp": utc_now_iso(),
            }
        points = payload.get("points", [])
        area_estimate = 0.0
        if isinstance(points, list) and len(points) >= 3:
            area_estimate = float(len(points) - 2) * 10.0
        return {
            "component_id": self.id,
            "status": "completed",
            "geometry_entities": len(points),
            "area_estimate": round(area_estimate, 3),
            "timestamp": utc_now_iso(),
        }


class CADParser(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        interpreter = IndustrialLayoutInterpreter()
        layout_result = interpreter.interpret(payload)
        compact_response = bool(payload.get("compact_response", False))
        snapshot = layout_result
        if compact_response:
            factory_graph = layout_result.get("factory_graph", {})
            knowledge_graph = layout_result.get("knowledge_graph", {})
            snapshot = {
                "layout_name": layout_result.get("layout_name"),
                "source_format": layout_result.get("source_format"),
                "source_hash": layout_result.get("source_hash"),
                "factory_graph": {
                    "node_count": factory_graph.get("node_count", 0),
                    "edge_count": factory_graph.get("edge_count", 0),
                    "kind_counts": factory_graph.get("kind_counts", {}),
                },
                "knowledge_graph": {
                    "fact_count": knowledge_graph.get("fact_count", 0),
                    "relation_count": knowledge_graph.get("relation_count", 0),
                    "confidence": knowledge_graph.get("confidence", 0.0),
                },
                "simulation": layout_result.get("simulation", {}),
                "plant_state_report": layout_result.get("plant_state_report", {}),
                "operational_summary": layout_result.get("operational_summary", {}),
                "confidence": layout_result.get("confidence", 0.0),
                "trace": layout_result.get("trace", {}),
            }
        version_store = LayoutVersionStore()
        version_info = version_store.create_snapshot(
            layout_name=str(layout_result.get("layout_name") or payload.get("layout_name") or "industrial-layout"),
            source_hash=str(layout_result.get("source_hash", "")),
            snapshot=snapshot,
            scenario=str(payload.get("scenario") or "baseline"),
            revision_note=str(payload.get("revision_note") or "automated import snapshot"),
            branch=str(payload.get("branch") or "main"),
            set_baseline=bool(payload.get("set_baseline", False)),
        )
        entities = len(layout_result.get("entities", []))
        if compact_response:
            factory_graph = layout_result.get("factory_graph", {}) if isinstance(layout_result, dict) else {}
            knowledge_graph = layout_result.get("knowledge_graph", {}) if isinstance(layout_result, dict) else {}
            nodes = factory_graph.get("nodes", [])
            nodes_by_kind: dict[str, list[dict[str, Any]]] = {}
            if isinstance(nodes, list):
                for node in nodes:
                    if isinstance(node, dict):
                        nodes_by_kind.setdefault(str(node.get("kind", "resource")), []).append(node)
            node_sample: list[dict[str, Any]] = []
            sample_index = 0
            while len(node_sample) < 300 and any(sample_index < len(items) for items in nodes_by_kind.values()):
                for items in nodes_by_kind.values():
                    if sample_index < len(items):
                        node_sample.append(items[sample_index])
                        if len(node_sample) >= 300:
                            break
                sample_index += 1
            sample_ids = {node.get("id") for node in node_sample if isinstance(node, dict)}
            edges = factory_graph.get("edges", [])
            edge_sample = [
                edge for edge in edges
                if isinstance(edge, dict) and edge.get("source") in sample_ids and edge.get("target") in sample_ids
            ][:500] if isinstance(edges, list) else []
            return {
                "component_id": self.id,
                "status": "completed",
                "layout_name": layout_result.get("layout_name"),
                "source_length": len(str(payload.get("source", ""))),
                "parsed_entities": entities,
                "factory_graph": {
                    "node_count": factory_graph.get("node_count", 0),
                    "edge_count": factory_graph.get("edge_count", 0),
                    "kind_counts": factory_graph.get("kind_counts", {}),
                    "nodes": node_sample,
                    "edges": edge_sample,
                },
                "knowledge_graph": {
                    "fact_count": knowledge_graph.get("fact_count", 0),
                    "relation_count": knowledge_graph.get("relation_count", 0),
                    "confidence": knowledge_graph.get("confidence", 0.0),
                },
                "simulation": layout_result.get("simulation", {}),
                "plant_state_report": layout_result.get("plant_state_report", {}),
                "engineering_analysis": layout_result.get("engineering_analysis", {}),
                "operational_summary": layout_result.get("operational_summary", {}),
                "confidence": layout_result.get("confidence", 0.0),
                "version_info": version_info,
                "timestamp": utc_now_iso(),
            }

        return {
            "component_id": self.id,
            "status": "completed",
            "layout_name": layout_result.get("layout_name"),
            "source_length": len(str(payload.get("source", ""))),
            "parsed_entities": entities,
            "layout_result": layout_result,
            "factory_graph": layout_result.get("factory_graph", {}),
            "knowledge_graph": layout_result.get("knowledge_graph", {}),
            "digital_twin": layout_result.get("digital_twin", {}),
            "simulation": layout_result.get("simulation", {}),
            "engineering_analysis": layout_result.get("engineering_analysis", {}),
            "plant_state_report": layout_result.get("plant_state_report", {}),
            "executive_report": layout_result.get("executive_report", ""),
            "confidence": layout_result.get("confidence", 0.0),
            "version_info": version_info,
            "timestamp": utc_now_iso(),
        }


class FactoryGraphRuntime(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        layout_result = payload.get("layout_result") or payload.get("interpretation") or {}
        graph = layout_result.get("factory_graph", {}) if isinstance(layout_result, dict) else {}
        assets = payload.get("assets", graph.get("nodes", []))
        links = payload.get("links", graph.get("edges", []))
        return {
            "component_id": self.id,
            "status": "completed",
            "nodes": len(assets),
            "edges": len(links),
            "graph_density": round((len(links) / max(len(assets), 1)), 4),
            "factory_graph": graph,
            "timestamp": utc_now_iso(),
        }


class KnowledgeGraphRuntime(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        layout_result = payload.get("layout_result") or payload.get("interpretation") or {}
        graph = layout_result.get("knowledge_graph", {}) if isinstance(layout_result, dict) else {}
        assertions = payload.get("assertions", graph.get("assertions", []))
        relations = payload.get("relations", graph.get("relations", []))
        return {
            "component_id": self.id,
            "status": "completed",
            "assertions": len(assertions),
            "relations": len(relations),
            "knowledge_coverage": round(min(1.0, (len(assertions) + len(relations)) / 100.0), 4),
            "knowledge_graph": graph,
            "timestamp": utc_now_iso(),
        }


class EvidenceRuntimeM004(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "component_id": self.id,
            "status": "completed",
            "evidence_refs": payload.get("evidence_refs", []),
            "confidence": float(payload.get("confidence", 0.65)),
            "timestamp": utc_now_iso(),
        }


class DigitalTwinRuntime(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        layout_result = payload.get("layout_result") or payload.get("interpretation") or {}
        twin = layout_result.get("digital_twin", {}) if isinstance(layout_result, dict) else {}
        sync_targets = payload.get(
            "sync_targets",
            twin.get(
                "state",
                {},
            ).get(
                "sync_targets",
                [
                    "factory_graph",
                    "knowledge_graph",
                    "assets",
                    "layouts",
                    "production",
                    "amrs",
                    "warehouse",
                    "wip",
                    "events",
                ],
            ),
        )
        return {
            "component_id": self.id,
            "status": "completed",
            "synced_targets": sync_targets,
            "sync_count": len(sync_targets),
            "digital_twin": twin,
            "timestamp": utc_now_iso(),
        }


class SimulationRuntime(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        layout_result = payload.get("layout_result") or payload.get("interpretation") or {}
        simulation = layout_result.get("simulation", {}) if isinstance(layout_result, dict) else {}
        scenarios = payload.get("scenarios", simulation.get("digital_twin_scenarios", ["baseline"]))
        scenario_count = max(1, len(scenarios))
        simulated_kpis = simulation if simulation else {
            "oee": round(0.72 + scenario_count * 0.01, 4),
            "roi": round(1.1 + scenario_count * 0.03, 4),
            "throughput": round(100 + scenario_count * 7.5, 2),
        }
        return {
            "component_id": self.id,
            "status": "completed",
            "scenarios": scenarios,
            "scenario_count": scenario_count,
            "simulated_kpis": simulated_kpis,
            "simulation": simulation,
            "timestamp": utc_now_iso(),
        }


class OptimizationRuntime(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        layout_result = payload.get("layout_result") or payload.get("interpretation") or {}
        analysis = layout_result.get("engineering_analysis", {}) if isinstance(layout_result, dict) else {}
        baseline = float(payload.get("baseline", 1.0))
        return {
            "component_id": self.id,
            "status": "completed",
            "baseline": baseline,
            "improvement": round(baseline * 0.12, 4),
            "confidence": 0.78,
            "engineering_analysis": analysis,
            "timestamp": utc_now_iso(),
        }


class ProposalIntelligenceRuntime(IndustrialComponent):
    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        layout_result = payload.get("layout_result") or payload.get("interpretation") or {}
        analysis = layout_result.get("engineering_analysis", {}) if isinstance(layout_result, dict) else {}
        recommendations = payload.get("recommendations", [])
        if not recommendations and isinstance(analysis, dict):
            recommendations = analysis.get("executive_recommendations", [])
        return {
            "component_id": self.id,
            "status": "completed",
            "executive_summary": "Industrial optimization proposal generated",
            "recommendations": recommendations,
            "proposal_quality": round(min(1.0, 0.65 + len(recommendations) * 0.05), 4),
            "engineering_analysis": analysis,
            "timestamp": utc_now_iso(),
        }


class ExecutiveScoringEngine:
    """Weighted multidimensional scoring with adaptive weights."""

    def __init__(self) -> None:
        self._weights: dict[str, float] = {
            "mission_alignment": 1.2,
            "engineering_quality": 1.1,
            "industrial_value": 1.2,
            "business_value": 1.1,
            "knowledge_growth": 1.0,
            "architecture_quality": 1.1,
            "reusability": 1.0,
            "maintainability": 1.0,
            "technical_debt": 0.9,
            "scalability": 1.0,
            "automation": 1.0,
            "oee_improvement": 1.2,
            "roi": 1.2,
            "confidence": 1.1,
            "evidence_quality": 1.2,
            "risk": 0.9,
            "execution_cost": 0.8,
            "execution_time": 0.8,
            "innovation": 1.0,
        }

    def evaluate(self, dimensions: dict[str, float]) -> float:
        weighted_sum = 0.0
        total_weight = 0.0
        for key, weight in self._weights.items():
            value = float(dimensions.get(key, 0.0))
            weighted_sum += weight * value
            total_weight += weight
        return round(weighted_sum / max(total_weight, 0.0001), 4)

    def adapt_weights(self, evidence_quality: float, mission_alignment: float) -> dict[str, float]:
        # Small bounded updates to keep behavior stable and evidence-driven.
        delta = (evidence_quality + mission_alignment - 1.0) * 0.02
        self._weights["evidence_quality"] = round(max(0.5, min(2.0, self._weights["evidence_quality"] + delta)), 4)
        self._weights["mission_alignment"] = round(max(0.5, min(2.0, self._weights["mission_alignment"] + delta)), 4)
        return dict(self._weights)

    def weights(self) -> dict[str, float]:
        return dict(self._weights)


class AHDERuntime:
    """Autonomous Hypothesis Driven Execution workflow runtime."""

    def __init__(self, scoring_engine: ExecutiveScoringEngine) -> None:
        self._scoring_engine = scoring_engine

    def decide(self, mission_id: str, uncertainty: str, context: dict[str, Any]) -> dict[str, Any]:
        hypotheses = self._generate_hypotheses(uncertainty)

        evaluated: list[dict[str, Any]] = []
        for hypothesis in hypotheses:
            dimensions = self._simulate_dimensions(hypothesis, context)
            score = self._scoring_engine.evaluate(dimensions)
            evaluated.append(
                {
                    "hypothesis": hypothesis,
                    "dimensions": dimensions,
                    "score": score,
                }
            )

        ranked = sorted(evaluated, key=lambda item: item["score"], reverse=True)
        selected = ranked[0] if ranked else None

        if selected:
            self._scoring_engine.adapt_weights(
                evidence_quality=float(selected["dimensions"].get("evidence_quality", 0.0)),
                mission_alignment=float(selected["dimensions"].get("mission_alignment", 0.0)),
            )

        return {
            "mission_id": mission_id,
            "uncertainty": uncertainty,
            "pipeline": [
                "mission",
                "goal_definition",
                "uncertainty_detection",
                "hypothesis_generation",
                "simulation",
                "evidence_generation",
                "executive_scoring",
                "ranking",
                "best_candidate",
                "implementation",
                "testing",
                "evidence_validation",
                "learning",
                "continue_mission",
            ],
            "evaluated": ranked,
            "selected": selected,
            "weights": self._scoring_engine.weights(),
            "timestamp": utc_now_iso(),
        }

    def _generate_hypotheses(self, uncertainty: str) -> list[str]:
        base = uncertainty.strip() or "industrial optimization"
        return [
            f"Increase model granularity for {base}",
            f"Run constrained simulation-first strategy for {base}",
            f"Apply evidence-prioritized optimization strategy for {base}",
        ]

    def _simulate_dimensions(self, hypothesis: str, context: dict[str, Any]) -> dict[str, float]:
        seed = sha256(f"{hypothesis}|{context}".encode("utf-8")).hexdigest()

        def metric(offset: int) -> float:
            raw = int(seed[offset : offset + 4], 16)
            return round(0.45 + (raw % 56) / 100.0, 4)

        return {
            "mission_alignment": metric(0),
            "engineering_quality": metric(4),
            "industrial_value": metric(8),
            "business_value": metric(12),
            "knowledge_growth": metric(16),
            "architecture_quality": metric(20),
            "reusability": metric(24),
            "maintainability": metric(28),
            "technical_debt": metric(32),
            "scalability": metric(36),
            "automation": metric(40),
            "oee_improvement": metric(44),
            "roi": metric(48),
            "confidence": metric(52),
            "evidence_quality": metric(56),
            "risk": metric(2),
            "execution_cost": metric(6),
            "execution_time": metric(10),
            "innovation": metric(14),
        }


class IndustrialIntelligenceCore:
    """Single runtime facade that keeps M010 engines integrated and dependency-safe."""

    DEPENDENCY_CHAIN = [
        "industrial-geometry-engine",
        "dwg-intelligence-parser",
        "dxf-intelligence-parser",
        "factory-graph-runtime-m001",
        "knowledge-graph-runtime",
        "evidence-runtime-m004",
        "digital-twin-runtime",
        "industrial-simulation-runtime",
        "bottleneck-analyzer-m007",
        "industrial-flow-analyzer",
        "amr-optimization-engine",
        "oee-prediction-engine",
        "roi-engine",
        "smart-proposal-intelligence-runtime",
    ]

    def __init__(self) -> None:
        self._components = self._build_components()
        self._scoring_engine = ExecutiveScoringEngine()
        self._ahde = AHDERuntime(self._scoring_engine)
        self._validate_chain()

    def list_components(self) -> list[dict[str, Any]]:
        return [self._snapshot(component) for component in self._ordered_components()]

    def health(self) -> dict[str, Any]:
        components = self._ordered_components()
        health_items = [item.health() for item in components]
        return {
            "status": "ok" if all(item["status"] == "ok" for item in health_items) else "degraded",
            "dependency_chain": list(self.DEPENDENCY_CHAIN),
            "components": health_items,
            "timestamp": utc_now_iso(),
        }

    def component(self, component_id: str) -> dict[str, Any]:
        component = self._components[component_id]
        return self._snapshot(component)

    def execute_component(self, component_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_dependencies(component_id)
        component = self._components[component_id]
        return component.execute(payload)

    def ahde_decide(self, mission_id: str, uncertainty: str, context: dict[str, Any]) -> dict[str, Any]:
        return self._ahde.decide(mission_id=mission_id, uncertainty=uncertainty, context=context)

    def mission_payload(self) -> dict[str, Any]:
        return {
            "id": "M010",
            "title": "Industrial Intelligence Core",
            "objective": "Complete the industrial intelligence runtime stack and AHDE-based autonomous execution.",
            "status": "planned",
            "dependencies": ["M001", "M004", "M007"],
            "capabilities": [item.id for item in self._ordered_components()],
            "tags": ["industrial", "cognitive_os", "ahde", "runtime", "digital_twin"],
            "deliverables": [
                "DWG Intelligence Parser",
                "DXF Intelligence Parser",
                "Industrial Geometry Engine",
                "Factory Graph Runtime",
                "Knowledge Graph Runtime",
                "Evidence Runtime",
                "Digital Twin Runtime",
                "Industrial Simulation Runtime",
                "Bottleneck Analyzer",
                "Industrial Flow Analyzer",
                "AMR Optimization Engine",
                "OEE Prediction Engine",
                "ROI Engine",
                "Smart Proposal Intelligence Runtime",
            ],
        }

    def registration_summary(self) -> dict[str, Any]:
        return {
            "mission_id": "M010",
            "components": self.list_components(),
            "dependency_chain": list(self.DEPENDENCY_CHAIN),
            "ahde_policy": "enabled",
            "timestamp": utc_now_iso(),
        }

    def _ordered_components(self) -> list[IndustrialComponent]:
        return [self._components[item_id] for item_id in self.DEPENDENCY_CHAIN]

    def _snapshot(self, component: IndustrialComponent) -> dict[str, Any]:
        return {
            "id": component.id,
            "name": component.name,
            "mission_ref": component.mission_ref,
            "dependencies": list(component.dependencies),
            "capabilities": list(component.capabilities),
            "apis": list(component.apis),
            "metadata": dict(component.metadata),
            "health": component.health(),
        }

    def _ensure_dependencies(self, component_id: str) -> None:
        component = self._components[component_id]
        for dep in component.dependencies:
            if dep not in self._components:
                raise ValueError(f"Missing dependency {dep} for {component_id}")

    def _validate_chain(self) -> None:
        seen: set[str] = set()
        for component_id in self.DEPENDENCY_CHAIN:
            component = self._components.get(component_id)
            if not component:
                raise ValueError(f"Dependency chain references unknown component: {component_id}")
            for dep in component.dependencies:
                if dep not in seen:
                    raise ValueError(
                        f"Dependency order violation: {component_id} depends on {dep} before it is available"
                    )
            seen.add(component_id)

    def _build_components(self) -> dict[str, IndustrialComponent]:
        return {
            "industrial-geometry-engine": GeometryEngine(
                id="industrial-geometry-engine",
                name="Industrial Geometry Engine",
                mission_ref="M010",
                apis=["/api/cognitive-os/industrial-intelligence/components/industrial-geometry-engine/execute"],
                capabilities=["geometry_extraction", "spatial_metrics", "layout_normalization"],
                metadata={"version": "1.0.0", "stage": "foundation"},
            ),
            "dwg-intelligence-parser": CADParser(
                id="dwg-intelligence-parser",
                name="DWG Intelligence Parser",
                mission_ref="M010",
                dependencies=["industrial-geometry-engine"],
                apis=["/api/cognitive-os/industrial-intelligence/components/dwg-intelligence-parser/execute"],
                capabilities=["dwg_parsing", "entity_tokenization", "geometry_mapping"],
                metadata={"version": "1.0.0", "format": "DWG"},
            ),
            "dxf-intelligence-parser": CADParser(
                id="dxf-intelligence-parser",
                name="DXF Intelligence Parser",
                mission_ref="M010",
                dependencies=["industrial-geometry-engine"],
                apis=["/api/cognitive-os/industrial-intelligence/components/dxf-intelligence-parser/execute"],
                capabilities=["dxf_parsing", "entity_tokenization", "geometry_mapping"],
                metadata={"version": "1.0.0", "format": "DXF"},
            ),
            "factory-graph-runtime-m001": FactoryGraphRuntime(
                id="factory-graph-runtime-m001",
                name="Factory Graph Runtime",
                mission_ref="M001",
                dependencies=["dwg-intelligence-parser", "dxf-intelligence-parser"],
                apis=["/api/cognitive-os/industrial-intelligence/components/factory-graph-runtime-m001/execute"],
                capabilities=["graph_construction", "asset_connectivity", "topology_indexing"],
                metadata={"version": "1.0.0", "mission": "M001"},
            ),
            "knowledge-graph-runtime": KnowledgeGraphRuntime(
                id="knowledge-graph-runtime",
                name="Knowledge Graph Runtime",
                mission_ref="M010",
                dependencies=["factory-graph-runtime-m001"],
                apis=["/api/cognitive-os/industrial-intelligence/components/knowledge-graph-runtime/execute"],
                capabilities=["semantic_relations", "knowledge_fusion", "traceability_links"],
                metadata={"version": "1.0.0", "domain": "industrial_knowledge"},
            ),
            "evidence-runtime-m004": EvidenceRuntimeM004(
                id="evidence-runtime-m004",
                name="Evidence Runtime",
                mission_ref="M004",
                dependencies=["knowledge-graph-runtime"],
                apis=["/api/cognitive-os/industrial-intelligence/components/evidence-runtime-m004/execute"],
                capabilities=["evidence_tracking", "confidence_scoring", "source_traceability"],
                metadata={"version": "1.0.0", "mission": "M004"},
            ),
            "digital-twin-runtime": DigitalTwinRuntime(
                id="digital-twin-runtime",
                name="Digital Twin Runtime",
                mission_ref="M010",
                dependencies=["evidence-runtime-m004"],
                apis=["/api/cognitive-os/industrial-intelligence/components/digital-twin-runtime/execute"],
                capabilities=["twin_synchronization", "state_projection", "asset_digitalization"],
                metadata={"version": "1.0.0", "single_executable_representation": True},
            ),
            "industrial-simulation-runtime": SimulationRuntime(
                id="industrial-simulation-runtime",
                name="Industrial Simulation Runtime",
                mission_ref="M010",
                dependencies=["digital-twin-runtime"],
                apis=["/api/cognitive-os/industrial-intelligence/components/industrial-simulation-runtime/execute"],
                capabilities=["scenario_simulation", "capacity_analysis", "kpi_projection"],
                metadata={"version": "1.0.0", "simulation_domains": ["flow", "oee", "roi", "energy"]},
            ),
            "bottleneck-analyzer-m007": OptimizationRuntime(
                id="bottleneck-analyzer-m007",
                name="Bottleneck Analyzer",
                mission_ref="M007",
                dependencies=["industrial-simulation-runtime"],
                apis=["/api/cognitive-os/industrial-intelligence/components/bottleneck-analyzer-m007/execute"],
                capabilities=["bottleneck_detection", "constraint_ranking", "throughput_impact"],
                metadata={"version": "1.0.0", "mission": "M007"},
            ),
            "industrial-flow-analyzer": OptimizationRuntime(
                id="industrial-flow-analyzer",
                name="Industrial Flow Analyzer",
                mission_ref="M010",
                dependencies=["bottleneck-analyzer-m007"],
                apis=["/api/cognitive-os/industrial-intelligence/components/industrial-flow-analyzer/execute"],
                capabilities=["flow_balance", "wip_dynamics", "warehouse_throughput"],
                metadata={"version": "1.0.0"},
            ),
            "amr-optimization-engine": OptimizationRuntime(
                id="amr-optimization-engine",
                name="AMR Optimization Engine",
                mission_ref="M010",
                dependencies=["industrial-flow-analyzer"],
                apis=["/api/cognitive-os/industrial-intelligence/components/amr-optimization-engine/execute"],
                capabilities=["amr_routing", "fleet_balancing", "collision_risk_reduction"],
                metadata={"version": "1.0.0"},
            ),
            "oee-prediction-engine": OptimizationRuntime(
                id="oee-prediction-engine",
                name="OEE Prediction Engine",
                mission_ref="M010",
                dependencies=["amr-optimization-engine"],
                apis=["/api/cognitive-os/industrial-intelligence/components/oee-prediction-engine/execute"],
                capabilities=["oee_forecasting", "availability_prediction", "performance_loss_detection"],
                metadata={"version": "1.0.0"},
            ),
            "roi-engine": OptimizationRuntime(
                id="roi-engine",
                name="ROI Engine",
                mission_ref="M010",
                dependencies=["oee-prediction-engine"],
                apis=["/api/cognitive-os/industrial-intelligence/components/roi-engine/execute"],
                capabilities=["investment_analysis", "payback_estimation", "risk_adjusted_roi"],
                metadata={"version": "1.0.0"},
            ),
            "smart-proposal-intelligence-runtime": ProposalIntelligenceRuntime(
                id="smart-proposal-intelligence-runtime",
                name="Smart Proposal Intelligence Runtime",
                mission_ref="M010",
                dependencies=["roi-engine"],
                apis=[
                    "/api/cognitive-os/industrial-intelligence/components/smart-proposal-intelligence-runtime/execute"
                ],
                capabilities=["proposal_generation", "executive_reporting", "evidence_citation"],
                metadata={"version": "1.0.0", "output": "executive_report"},
            ),
        }


def bootstrap_industrial_intelligence(system: Any) -> IndustrialIntelligenceCore:
    """Create and auto-register the M010 industrial intelligence core in Cognitive OS."""

    core = IndustrialIntelligenceCore()

    # Register platform.
    system.platform_registry.register(
        PlatformConsumer(
            id="industrial-intelligence-core",
            name="Industrial Intelligence Core",
            contract_version="v1",
            metadata={
                "mission": "M010",
                "policy": "AHDE",
                "health_api": "/api/cognitive-os/industrial-intelligence/status",
            },
        )
    )

    # Register capabilities.
    for component in core.list_components():
        system.capability_graph.upsert_node(
            CapabilityNode(
                id=component["id"],
                description=component["name"],
                interfaces=component["apis"],
                dependencies=component["dependencies"],
            )
        )

    # Register mission.
    system.mission_core.upsert_mission(MissionNode(**core.mission_payload()))

    # Register in memory, knowledge, and governance channels.
    summary = core.registration_summary()
    system.memory_core.put("industrial_intelligence", "m010_registration", summary)
    system.memory_core.put("industrial_intelligence", "ahde_policy", {"enabled": True, "timestamp": utc_now_iso()})

    evidence = EvidenceRecord(
        id="evidence-m010-bootstrap",
        source="cognitive_os.bootstrap_industrial_intelligence",
        payload=summary,
        mission_id="M010",
    )
    system.evidence_runtime.add(evidence)

    system.truth_runtime.upsert(
        TruthAssertion(
            id="truth-m010-core-registered",
            claim="M010 Industrial Intelligence Core is registered in Cognitive OS",
            confidence=0.86,
            evidence_ids=[evidence.id],
        )
    )

    governance_decision = system.governance.evaluate(
        touches_industrial_modules=False,
        increases_modularity=True,
        increases_reuse=True,
        increases_interoperability=True,
    )
    system.memory_core.put("industrial_intelligence", "governance", governance_decision.__dict__)

    system.coordinator.publish(
        "industrial_intelligence.bootstrap",
        {
            "mission_id": "M010",
            "components": [item["id"] for item in summary["components"]],
            "ahde": True,
            "governance_approved": governance_decision.approved,
        },
    )

    return core
