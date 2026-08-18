"""Reusable runtimes for evidence, truth, hypotheses, scoring, and validation."""

from __future__ import annotations

from cognitive_os.models import EvidenceRecord, Hypothesis, HypothesisStatus, ScoreCard, TruthAssertion


class EvidenceRuntime:
    def __init__(self) -> None:
        self._evidence: dict[str, EvidenceRecord] = {}

    def add(self, evidence: EvidenceRecord) -> None:
        self._evidence[evidence.id] = evidence

    def get(self, evidence_id: str) -> EvidenceRecord | None:
        return self._evidence.get(evidence_id)

    def list(self) -> list[EvidenceRecord]:
        return list(self._evidence.values())


class TruthRuntime:
    def __init__(self, evidence_runtime: EvidenceRuntime) -> None:
        self._truth: dict[str, TruthAssertion] = {}
        self._evidence_runtime = evidence_runtime

    def upsert(self, assertion: TruthAssertion) -> TruthAssertion:
        has_support = any(self._evidence_runtime.get(eid) for eid in assertion.evidence_ids)
        assertion.status = "supported" if has_support else "provisional"
        self._truth[assertion.id] = assertion
        return assertion

    def list(self) -> list[TruthAssertion]:
        return list(self._truth.values())


class HypothesisEngine:
    def __init__(self) -> None:
        self._items: dict[str, Hypothesis] = {}

    def submit(self, hypothesis: Hypothesis) -> None:
        self._items[hypothesis.id] = hypothesis

    def list_for_mission(self, mission_id: str) -> list[Hypothesis]:
        return [h for h in self._items.values() if h.mission_id == mission_id]

    def list_actionable_for_mission(self, mission_id: str) -> list[Hypothesis]:
        terminal = {HypothesisStatus.VALIDATED, HypothesisStatus.REJECTED}
        return [h for h in self.list_for_mission(mission_id) if h.status not in terminal]

    def update_status(self, hypothesis_id: str, status: HypothesisStatus) -> None:
        item = self._items.get(hypothesis_id)
        if item:
            item.status = status


class ScoringEngine:
    """Computes global mission value with optional mission-specific weights."""

    def __init__(self) -> None:
        self._weights = {
            "architecture": 1.25,
            "maintainability": 1.15,
            "scalability": 1.10,
            "performance": 1.0,
            "interoperability": 1.35,
            "governance": 1.15,
            "mission_alignment": 1.40,
            "engineering_quality": 1.10,
            "business_value": 1.20,
            "knowledge_value": 1.10,
            "industrial_value": 1.20,
            "roi": 1.05,
            "risk_inverse": 1.25,
            "reuse": 1.15,
            "automation": 1.0,
            "testing": 1.15,
            "documentation": 0.75,
            "evidence_quality": 1.30,
            "confidence": 1.20,
            "execution_cost_inverse": 0.85,
            "execution_time_inverse": 0.80,
            "technical_debt_inverse": 0.90,
            "innovation": 0.65,
        }

    def score(self, card: ScoreCard, weights: dict[str, float] | None = None) -> float:
        dimensions = card.dimensions()
        effective_weights = dict(self._weights)
        if weights:
            effective_weights.update(
                {key: max(0.0, float(value)) for key, value in weights.items() if key in dimensions}
            )
        weighted_sum = sum(dimensions[key] * effective_weights.get(key, 1.0) for key in dimensions)
        total_weight = sum(effective_weights.get(key, 1.0) for key in dimensions)
        return round(weighted_sum / total_weight, 4)


class ValidationEngine:
    """Simple policy gate to approve only positive engineering actions."""

    def __init__(self, min_score: float = 0.65) -> None:
        self._min_score = min_score

    def validate(self, score: float, no_business_module_change: bool) -> tuple[bool, str]:
        if not no_business_module_change:
            return False, "Rejected: proposed action touches industrial business modules"
        if score < self._min_score:
            return False, f"Rejected: score {score:.3f} below threshold {self._min_score:.3f}"
        return True, "Validated"
