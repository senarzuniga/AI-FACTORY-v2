"""Core domain models for the AI-FACTORY Cognitive Operating System."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MissionStatus(str, Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    ACTIVE = "active"
    BLOCKED = "blocked"
    VALIDATION = "validation"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class HypothesisStatus(str, Enum):
    PROPOSED = "proposed"
    SCORED = "scored"
    SELECTED = "selected"
    VALIDATED = "validated"
    REJECTED = "rejected"


@dataclass
class AgentProfile:
    id: str
    name: str
    capabilities: list[str] = field(default_factory=list)
    runtime: str = "python"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformConsumer:
    id: str
    name: str
    contract_version: str = "v1"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RepositoryNode:
    id: str
    path: str
    status: str
    purpose: str = ""
    capabilities: list[str] = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)
    apis: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    instructions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    known_gaps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeNode:
    id: str
    topic: str
    statement: str
    classification: str
    source: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    validation_status: str = "provisional"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityNode:
    id: str
    description: str
    interfaces: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class MissionObjective:
    id: str
    statement: str
    owner: str = ""
    priority: int = 3


@dataclass
class StrategicAlignment:
    themes: list[str] = field(default_factory=list)
    target_platforms: list[str] = field(default_factory=lambda: ["IS_BACKOFFICE", "ING_DIGHUB"])
    rationale: str = ""


@dataclass
class MissionValue:
    business_value: float = 0.0
    engineering_value: float = 0.0
    knowledge_value: float = 0.0


@dataclass
class WorkPackage:
    id: str
    title: str
    status: str = "planned"
    owner: str = ""
    depends_on: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)


@dataclass
class MissionRisk:
    id: str
    description: str
    probability: float = 0.0
    impact: float = 0.0
    mitigation: str = ""


@dataclass
class KPI:
    id: str
    name: str
    target: float
    current: float = 0.0
    unit: str = ""


@dataclass
class Milestone:
    id: str
    name: str
    due_at: str
    status: str = "planned"


@dataclass
class QualityGate:
    id: str
    description: str
    status: str = "pending"
    mandatory: bool = True
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class MissionGap:
    id: str
    statement: str
    priority: int = 3
    status: str = "open"
    executable: bool = True
    required_capability: str = ""


@dataclass
class CascadeAction:
    id: str
    description: str
    gap_id: str = ""
    capability_id: str = ""
    status: str = "planned"
    priority_score: float = 0.0


@dataclass
class MissionHistoryEvent:
    timestamp: str
    event_type: str
    detail: str
    actor: str = "system"


@dataclass
class MissionEvolution:
    version: int
    change_summary: str
    changed_at: str = field(default_factory=utc_now_iso)


@dataclass
class MissionScoringMatrix:
    architecture: float = 0.0
    maintainability: float = 0.0
    scalability: float = 0.0
    performance: float = 0.0
    interoperability: float = 0.0
    governance: float = 0.0

    def global_score(self) -> float:
        values = [
            self.architecture,
            self.maintainability,
            self.scalability,
            self.performance,
            self.interoperability,
            self.governance,
        ]
        return round(sum(values) / len(values), 4)


@dataclass
class MissionTraceability:
    source_documents: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    dependency_links: list[str] = field(default_factory=list)


@dataclass
class MissionKnowledgeAsset:
    id: str
    asset_type: str
    uri: str
    description: str = ""


@dataclass
class MissionNode:
    id: str
    title: str
    objective: str
    status: MissionStatus = MissionStatus.DRAFT
    objectives: list[MissionObjective] = field(default_factory=list)
    strategic_alignment: StrategicAlignment = field(default_factory=StrategicAlignment)
    value: MissionValue = field(default_factory=MissionValue)
    hypothesis_portfolio_ids: list[str] = field(default_factory=list)
    scoring_matrix: MissionScoringMatrix = field(default_factory=MissionScoringMatrix)
    scoring_weights: dict[str, float] = field(default_factory=dict)
    executive_scorecard: dict[str, float] = field(default_factory=dict)
    work_packages: list[WorkPackage] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    risks: list[MissionRisk] = field(default_factory=list)
    kpis: list[KPI] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
    quality_gates: list[QualityGate] = field(default_factory=list)
    gaps: list[MissionGap] = field(default_factory=list)
    next_actions: list[CascadeAction] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    mission_state: str = "initialized"
    mission_history: list[MissionHistoryEvent] = field(default_factory=list)
    mission_evolution: list[MissionEvolution] = field(default_factory=list)
    mission_score: float = 0.0
    mission_roi: float = 0.0
    mission_confidence: float = 0.0
    mission_traceability: MissionTraceability = field(default_factory=MissionTraceability)
    mission_knowledge_assets: list[MissionKnowledgeAsset] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = MissionStatus(self.status)
            except ValueError:
                self.status = MissionStatus.DRAFT

        self.objectives = [
            objective if isinstance(objective, MissionObjective) else MissionObjective(**objective)
            for objective in self.objectives
        ]
        if isinstance(self.strategic_alignment, dict):
            self.strategic_alignment = StrategicAlignment(**self.strategic_alignment)
        if isinstance(self.value, dict):
            self.value = MissionValue(**self.value)
        if isinstance(self.scoring_matrix, dict):
            self.scoring_matrix = MissionScoringMatrix(**self.scoring_matrix)

        self.work_packages = [
            package if isinstance(package, WorkPackage) else WorkPackage(**package)
            for package in self.work_packages
        ]
        self.risks = [risk if isinstance(risk, MissionRisk) else MissionRisk(**risk) for risk in self.risks]
        self.kpis = [kpi if isinstance(kpi, KPI) else KPI(**kpi) for kpi in self.kpis]
        self.milestones = [
            milestone if isinstance(milestone, Milestone) else Milestone(**milestone)
            for milestone in self.milestones
        ]
        self.quality_gates = [
            gate if isinstance(gate, QualityGate) else QualityGate(**gate)
            for gate in self.quality_gates
        ]
        self.gaps = [gap if isinstance(gap, MissionGap) else MissionGap(**gap) for gap in self.gaps]
        self.next_actions = [
            action if isinstance(action, CascadeAction) else CascadeAction(**action)
            for action in self.next_actions
        ]
        self.mission_history = [
            event if isinstance(event, MissionHistoryEvent) else MissionHistoryEvent(**event)
            for event in self.mission_history
        ]
        self.mission_evolution = [
            evolution if isinstance(evolution, MissionEvolution) else MissionEvolution(**evolution)
            for evolution in self.mission_evolution
        ]
        if isinstance(self.mission_traceability, dict):
            self.mission_traceability = MissionTraceability(**self.mission_traceability)
        self.mission_knowledge_assets = [
            asset if isinstance(asset, MissionKnowledgeAsset) else MissionKnowledgeAsset(**asset)
            for asset in self.mission_knowledge_assets
        ]


@dataclass
class EvidenceRecord:
    id: str
    source: str
    payload: dict[str, Any]
    timestamp: str = field(default_factory=utc_now_iso)
    mission_id: str | None = None


@dataclass
class TruthAssertion:
    id: str
    claim: str
    confidence: float
    evidence_ids: list[str] = field(default_factory=list)
    status: str = "provisional"
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass
class Hypothesis:
    id: str
    mission_id: str
    statement: str
    expected_value: float
    implementation_plan: list[str] = field(default_factory=list)
    score: float = 0.0
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    rationale: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class ScoreCard:
    architecture: float
    maintainability: float
    scalability: float
    performance: float
    interoperability: float
    governance: float

    mission_alignment: float = 0.0
    engineering_quality: float = 0.0
    business_value: float = 0.0
    knowledge_value: float = 0.0
    industrial_value: float = 0.0
    roi: float = 0.0
    risk_inverse: float = 0.0
    reuse: float = 0.0
    automation: float = 0.0
    testing: float = 0.0
    documentation: float = 0.0
    evidence_quality: float = 0.0
    confidence: float = 0.0
    execution_cost_inverse: float = 0.0
    execution_time_inverse: float = 0.0
    technical_debt_inverse: float = 0.0
    innovation: float = 0.0

    def composite(self) -> float:
        values = list(self.dimensions().values())
        return sum(values) / len(values)

    def dimensions(self) -> dict[str, float]:
        return {
            key: max(0.0, min(1.0, float(value)))
            for key, value in self.__dict__.items()
        }


@dataclass
class GovernanceDecision:
    approved: bool
    reason: str
    policy_violations: list[str] = field(default_factory=list)


@dataclass
class ExecutionResult:
    selected_hypothesis_id: str | None
    validated: bool
    score: float
    reason: str
    executed_steps: list[str] = field(default_factory=list)
    mission_complete: bool = False
    next_actions: list[dict[str, Any]] = field(default_factory=list)
