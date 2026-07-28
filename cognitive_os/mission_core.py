"""Mission Manager Core for lifecycle and engineering decision workflow."""

from __future__ import annotations

from dataclasses import asdict

from cognitive_os.governance import Governance
from cognitive_os.models import (
    ExecutionResult,
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
        hypotheses = self._hypothesis_engine.list_for_mission(mission_id)
        if not hypotheses:
            return ExecutionResult(
                selected_hypothesis_id=None,
                validated=False,
                score=0.0,
                reason="No hypotheses submitted",
            )

        scored: list[tuple[Hypothesis, float]] = []
        for item in hypotheses:
            card = self._scorecard_from_hypothesis(item)
            value = self._scoring_engine.score(card)
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
            if mission:
                mission.status = MissionStatus.COMPLETED
                mission.mission_state = "completed"
                mission.mission_score = score
                mission.mission_confidence = min(1.0, score + 0.05)
                mission.mission_roi = round(
                    mission.value.business_value * 0.5
                    + mission.value.engineering_value * 0.35
                    + mission.value.knowledge_value * 0.15,
                    4,
                )
                card = self._scorecard_from_hypothesis(selected)
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
                        change_summary="Mission completed via validated hypothesis selection",
                    )
                )
                if self._mission_registry:
                    self._mission_registry.upsert(mission)
            return ExecutionResult(
                selected_hypothesis_id=selected.id,
                validated=True,
                score=score,
                reason=reason,
                executed_steps=selected.implementation_plan,
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

    @staticmethod
    def _scorecard_from_hypothesis(hypothesis: Hypothesis) -> ScoreCard:
        # Deterministic baseline scoring from hypothesis expected value and plan quality.
        plan_factor = min(len(hypothesis.implementation_plan) / 5.0, 1.0)
        base = max(0.0, min(hypothesis.expected_value, 1.0))
        return ScoreCard(
            architecture=round(min(1.0, base + 0.10 * plan_factor), 4),
            maintainability=round(min(1.0, base + 0.06 * plan_factor), 4),
            scalability=round(min(1.0, base + 0.05 * plan_factor), 4),
            performance=round(min(1.0, base + 0.03 * plan_factor), 4),
            interoperability=round(min(1.0, base + 0.12 * plan_factor), 4),
            governance=round(min(1.0, base + 0.08 * plan_factor), 4),
        )
