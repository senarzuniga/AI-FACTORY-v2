"""Mission Manager Core for lifecycle and engineering decision workflow."""

from __future__ import annotations

from dataclasses import asdict

from cognitive_os.governance import Governance
from cognitive_os.models import (
    ExecutionResult,
    CascadeAction,
    Hypothesis,
    HypothesisStatus,
    MissionHistoryEvent,
    MissionNode,
    MissionStatus,
    MissionEvolution,
    ScoreCard,
    utc_now_iso,
)
from cognitive_os.registries import MissionGraph, MissionRegistry
from cognitive_os.runtimes import HypothesisEngine, ScoringEngine, ValidationEngine


class MissionManagerCore:
    def __init__(
        self,
        mission_graph: MissionGraph,
        hypothesis_engine: HypothesisEngine,
        scoring_engine: ScoringEngine,
        validation_engine: ValidationEngine,
        governance: Governance,
        mission_registry: MissionRegistry | None = None,
    ) -> None:
        self._mission_graph = mission_graph
        self._hypothesis_engine = hypothesis_engine
        self._scoring_engine = scoring_engine
        self._validation_engine = validation_engine
        self._governance = governance
        self._mission_registry = mission_registry

    def upsert_mission(self, mission: MissionNode) -> None:
        mission.updated_at = utc_now_iso()
        mission.mission_history.append(
            MissionHistoryEvent(
                timestamp=utc_now_iso(),
                event_type="mission_upserted",
                detail="Mission stored in canonical mission manager",
            )
        )
        self._mission_graph.upsert(mission)
        if self._mission_registry:
            self._mission_registry.upsert(mission)

    def list_missions(self) -> list[MissionNode]:
        return self._mission_graph.list()

    def activate_unblocked(self) -> list[str]:
        activated: list[str] = []
        for mission in self._mission_graph.list():
            if mission.status == MissionStatus.DRAFT and self._mission_graph.is_unblocked(mission.id):
                mission.status = MissionStatus.ACTIVE
                mission.mission_state = "active"
                mission.updated_at = utc_now_iso()
                mission.mission_history.append(
                    MissionHistoryEvent(
                        timestamp=utc_now_iso(),
                        event_type="mission_activated",
                        detail="Mission moved from draft to active after dependency check",
                    )
                )
                if self._mission_registry:
                    self._mission_registry.upsert(mission)
                activated.append(mission.id)
        return activated

    def evaluate_mission_hypotheses(self, mission_id: str) -> ExecutionResult:
        mission = self._mission_graph.get(mission_id)
        hypotheses = self._hypothesis_engine.list_actionable_for_mission(mission_id)
        if not hypotheses:
            next_actions = self._ensure_continuation_actions(mission) if mission else []
            return ExecutionResult(
                selected_hypothesis_id=None,
                validated=False,
                score=0.0,
                reason="No actionable hypotheses; continuation actions remain" if next_actions else "No hypotheses submitted",
                mission_complete=bool(mission and mission.status == MissionStatus.COMPLETED),
                next_actions=[asdict(action) for action in next_actions],
            )

        scored: list[tuple[Hypothesis, float]] = []
        for item in hypotheses:
            card = self._scorecard_from_hypothesis(item)
            value = self._scoring_engine.score(card, mission.scoring_weights if mission else None)
            item.score = value
            scored.append((item, value))

        selected, score = max(scored, key=lambda pair: pair[1])
        self._hypothesis_engine.update_status(selected.id, HypothesisStatus.SELECTED)

        # Governance guardrail before validation threshold gate.
        gov = self._governance.evaluate(
            touches_industrial_modules=False,
            increases_modularity=True,
            increases_reuse=True,
            increases_interoperability=True,
        )
        if not gov.approved:
            self._hypothesis_engine.update_status(selected.id, HypothesisStatus.REJECTED)
            return ExecutionResult(
                selected_hypothesis_id=selected.id,
                validated=False,
                score=score,
                reason=f"Governance rejected: {','.join(gov.policy_violations)}",
            )

        validated, reason = self._validation_engine.validate(
            score=score,
            no_business_module_change=True,
        )
        if validated:
            self._hypothesis_engine.update_status(selected.id, HypothesisStatus.VALIDATED)
            mission = self._mission_graph.get(mission_id)
            mission_complete = False
            next_actions: list[CascadeAction] = []
            if mission:
                mission.mission_score = score
                mission.mission_confidence = min(1.0, score + 0.05)
                mission.mission_roi = round(
                    mission.value.business_value * 0.5
                    + mission.value.engineering_value * 0.35
                    + mission.value.knowledge_value * 0.15,
                    4,
                )
                card = self._scorecard_from_hypothesis(selected)
                mission.executive_scorecard = card.dimensions()
                mission.scoring_matrix.architecture = card.architecture
                mission.scoring_matrix.maintainability = card.maintainability
                mission.scoring_matrix.scalability = card.scalability
                mission.scoring_matrix.performance = card.performance
                mission.scoring_matrix.interoperability = card.interoperability
                mission.scoring_matrix.governance = card.governance
                mission.updated_at = utc_now_iso()
                mission.mission_history.append(
                    MissionHistoryEvent(
                        timestamp=utc_now_iso(),
                        event_type="mission_validated",
                        detail=f"Hypothesis {selected.id} validated with score {score:.4f}",
                    )
                )
                mission.mission_evolution.append(
                    MissionEvolution(
                        version=max(1, len(mission.mission_evolution) + 1),
                        change_summary="Validated hypothesis applied to mission readiness evaluation",
                    )
                )
                next_actions = self._ensure_continuation_actions(mission)
                mission_complete = not next_actions
                if mission_complete:
                    mission.status = MissionStatus.COMPLETED
                    mission.mission_state = "completed"
                else:
                    mission.status = MissionStatus.ACTIVE
                    mission.mission_state = "continuation_required"
                    mission.mission_history.append(
                        MissionHistoryEvent(
                            timestamp=utc_now_iso(),
                            event_type="mission_continuation_required",
                            detail=f"{len(next_actions)} executable action(s) remain after hypothesis validation",
                        )
                    )
                if self._mission_registry:
                    self._mission_registry.upsert(mission)
            return ExecutionResult(
                selected_hypothesis_id=selected.id,
                validated=True,
                score=score,
                reason=reason if mission_complete else f"{reason}; mission quality gates remain open",
                executed_steps=selected.implementation_plan,
                mission_complete=mission_complete,
                next_actions=[asdict(action) for action in next_actions],
            )

        self._hypothesis_engine.update_status(selected.id, HypothesisStatus.REJECTED)
        mission = self._mission_graph.get(mission_id)
        if mission:
            mission.status = MissionStatus.BLOCKED
            mission.mission_state = "blocked"
            mission.updated_at = utc_now_iso()
            mission.mission_history.append(
                MissionHistoryEvent(
                    timestamp=utc_now_iso(),
                    event_type="mission_rejected",
                    detail=f"Hypothesis {selected.id} rejected during validation",
                )
            )
            if self._mission_registry:
                self._mission_registry.upsert(mission)
        return ExecutionResult(
            selected_hypothesis_id=selected.id,
            validated=False,
            score=score,
            reason=reason,
        )

    def snapshot(self) -> dict:
        return {
            "missions": [asdict(mission) for mission in self._mission_graph.list()],
        }

    def refresh_readiness(self, mission_id: str) -> list[CascadeAction]:
        mission = self._mission_graph.get(mission_id)
        if not mission:
            return []
        actions = self._ensure_continuation_actions(mission)
        if actions and mission.status != MissionStatus.BLOCKED:
            mission.status = MissionStatus.ACTIVE
            mission.mission_state = "continuation_required"
        if self._mission_registry:
            self._mission_registry.upsert(mission)
        return actions

    @staticmethod
    def _ensure_continuation_actions(mission: MissionNode) -> list[CascadeAction]:
        existing = {action.id: action for action in mission.next_actions if action.status != "completed"}
        required: list[CascadeAction] = []

        for gap in mission.gaps:
            if gap.status != "closed" and gap.executable:
                action_id = f"{mission.id}-close-gap-{gap.id}"
                required.append(
                    existing.get(action_id)
                    or CascadeAction(
                        id=action_id,
                        description=f"Close mission gap: {gap.statement}",
                        gap_id=gap.id,
                        capability_id=gap.required_capability,
                        priority_score=round(max(0.0, min(1.0, gap.priority / 5.0)), 4),
                    )
                )

        for gate in mission.quality_gates:
            evidence_present = bool(gate.evidence_ids) and all(
                evidence_id in mission.evidence_ids for evidence_id in gate.evidence_ids
            )
            if gate.status == "passed" or (evidence_present and gate.status != "failed"):
                gate.status = "passed"
                continue
            if gate.mandatory:
                action_id = f"{mission.id}-pass-gate-{gate.id}"
                required.append(
                    existing.get(action_id)
                    or CascadeAction(
                        id=action_id,
                        description=f"Collect evidence and pass quality gate: {gate.description}",
                        priority_score=1.0,
                    )
                )

        for package in mission.work_packages:
            if package.status not in {"completed", "validated"}:
                action_id = f"{mission.id}-complete-package-{package.id}"
                required.append(
                    existing.get(action_id)
                    or CascadeAction(
                        id=action_id,
                        description=f"Complete work package: {package.title}",
                        priority_score=0.8,
                    )
                )

        required.sort(key=lambda action: action.priority_score, reverse=True)
        mission.next_actions = required
        return required

    @staticmethod
    def _scorecard_from_hypothesis(hypothesis: Hypothesis) -> ScoreCard:
        # Deterministic baseline scoring from hypothesis expected value and plan quality.
        plan_factor = min(len(hypothesis.implementation_plan) / 5.0, 1.0)
        base = max(0.0, min(hypothesis.expected_value, 1.0))
        dimensions = {
            "architecture": round(min(1.0, base + 0.10 * plan_factor), 4),
            "maintainability": round(min(1.0, base + 0.06 * plan_factor), 4),
            "scalability": round(min(1.0, base + 0.05 * plan_factor), 4),
            "performance": round(min(1.0, base + 0.03 * plan_factor), 4),
            "interoperability": round(min(1.0, base + 0.12 * plan_factor), 4),
            "governance": round(min(1.0, base + 0.08 * plan_factor), 4),
            "mission_alignment": base,
            "engineering_quality": min(1.0, base + 0.08 * plan_factor),
            "business_value": base,
            "knowledge_value": min(1.0, base + 0.04 * plan_factor),
            "industrial_value": base,
            "roi": base,
            "risk_inverse": max(0.0, min(1.0, base)),
            "reuse": min(1.0, base + 0.06 * plan_factor),
            "automation": min(1.0, base + 0.05 * plan_factor),
            "testing": min(1.0, base + 0.05 * plan_factor),
            "documentation": base,
            "evidence_quality": base,
            "confidence": base,
            "execution_cost_inverse": base,
            "execution_time_inverse": base,
            "technical_debt_inverse": base,
            "innovation": base,
        }
        dimensions.update({key: max(0.0, min(1.0, value)) for key, value in hypothesis.metrics.items() if key in dimensions})
        return ScoreCard(**dimensions)
