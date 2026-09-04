"""Mission model alternatives and automatic selection engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelHypothesis:
    id: str
    title: str
    description: str
    modularity: float
    reuse: float
    interoperability: float
    migration_safety: float
    governance_strength: float
    operational_complexity_inverse: float

    def score(self) -> float:
        return round(
            (
                self.modularity * 0.22
                + self.reuse * 0.18
                + self.interoperability * 0.22
                + self.migration_safety * 0.15
                + self.governance_strength * 0.15
                + self.operational_complexity_inverse * 0.08
            ),
            4,
        )


class MissionModelSelector:
    """Generates candidate canonical models and selects highest-scoring alternative."""

    def generate_hypotheses(self) -> list[ModelHypothesis]:
        return [
            ModelHypothesis(
                id="H1",
                title="Flat Mission Record",
                description="Single flat mission entity with denormalized lifecycle fields.",
                modularity=0.58,
                reuse=0.62,
                interoperability=0.61,
                migration_safety=0.91,
                governance_strength=0.63,
                operational_complexity_inverse=0.90,
            ),
            ModelHypothesis(
                id="H2",
                title="Normalized Mission Aggregate",
                description="Mission aggregate with structured sub-entities and explicit lifecycle state machine.",
                modularity=0.90,
                reuse=0.89,
                interoperability=0.92,
                migration_safety=0.83,
                governance_strength=0.91,
                operational_complexity_inverse=0.62,
            ),
            ModelHypothesis(
                id="H3",
                title="Event-Sourced Mission Ledger",
                description="Mission as append-only events with projection views.",
                modularity=0.93,
                reuse=0.85,
                interoperability=0.88,
                migration_safety=0.68,
                governance_strength=0.95,
                operational_complexity_inverse=0.45,
            ),
            ModelHypothesis(
                id="H4",
                title="Graph-Only Mission Semantics",
                description="All mission semantics encoded as graph nodes/edges without canonical aggregate.",
                modularity=0.72,
                reuse=0.78,
                interoperability=0.75,
                migration_safety=0.70,
                governance_strength=0.69,
                operational_complexity_inverse=0.58,
            ),
            ModelHypothesis(
                id="H5",
                title="Dual-Layer Canonical + Compatibility",
                description="Canonical normalized aggregate with compatibility adapters for legacy mission formats.",
                modularity=0.94,
                reuse=0.93,
                interoperability=0.95,
                migration_safety=0.92,
                governance_strength=0.90,
                operational_complexity_inverse=0.70,
            ),
            ModelHypothesis(
                id="H6",
                title="Domain-Split Mission Microtypes",
                description="Separate mission records by domain with orchestration-level federation.",
                modularity=0.86,
                reuse=0.79,
                interoperability=0.82,
                migration_safety=0.74,
                governance_strength=0.87,
                operational_complexity_inverse=0.57,
            ),
        ]

    def select_best(self) -> dict:
        hypotheses = self.generate_hypotheses()
        scored = [
            {
                "id": hypothesis.id,
                "title": hypothesis.title,
                "description": hypothesis.description,
                "score": hypothesis.score(),
            }
            for hypothesis in hypotheses
        ]
        winner = max(scored, key=lambda item: item["score"])
        return {
            "hypotheses": sorted(scored, key=lambda item: item["score"], reverse=True),
            "selected": winner,
            "production_ready": winner["score"] >= 0.85,
        }
