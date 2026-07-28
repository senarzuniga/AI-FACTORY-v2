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

    def update_status(self, hypothesis_id: str, status: HypothesisStatus) -> None:
        item = self._items.get(hypothesis_id)
        if item:
            item.status = status


class ScoringEngine:
    """Computes engineering score using weights that favor modularity and interoperability."""

    def __init__(self) -> None:
        self._weights = {
            "architecture": 1.25,
            "maintainability": 1.15,
            "scalability": 1.10,
            "performance": 1.0,
            "interoperability": 1.35,
            "governance": 1.15,
        }

    def score(self, card: ScoreCard) -> float:
        weighted_sum = (
            card.architecture * self._weights["architecture"]
            + card.maintainability * self._weights["maintainability"]
            + card.scalability * self._weights["scalability"]
            + card.performance * self._weights["performance"]
            + card.interoperability * self._weights["interoperability"]
            + card.governance * self._weights["governance"]
        )
        total_weight = sum(self._weights.values())
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
