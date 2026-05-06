"""
JUDGE AGENT
Evalua y selecciona la mejor generacion entre multiples candidatos.
Mejora brutal de calidad mediante comparacion competitiva.
"""

from __future__ import annotations

from typing import Any, Dict, List


class JudgeAgent:
    """Evalua candidatos y selecciona el de mayor calidad."""

    criteria_weights: Dict[str, float] = {
        "completeness": 0.25,
        "coherence": 0.25,
        "relevance": 0.20,
        "quality": 0.20,
        "style_match": 0.10,
    }

    async def evaluate(
        self, candidates: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        scored = [
            {"candidate": c, "score": self._score_candidate(c, context)}
            for c in candidates
        ]
        best = max(scored, key=lambda x: x["score"])
        return {
            "selected": best["candidate"],
            "all_scores": scored,
            "improvement_suggestions": self._generate_suggestions(scored),
        }

    def _score_candidate(self, candidate: Dict[str, Any], context: Dict[str, Any]) -> float:  # noqa: ARG002
        score = 0.0
        content = candidate.get("content", "")
        score += self.criteria_weights["completeness"] * (
            1.0 if all(k in candidate for k in ("content", "metadata", "sources")) else 0.5
        )
        score += self.criteria_weights["coherence"] * (1.0 if len(content) > 50 else 0.4)
        score += self.criteria_weights["relevance"] * 1.0
        score += self.criteria_weights["quality"] * (1.0 if len(content) > 100 else 0.6)
        style = candidate.get("style", "")
        score += self.criteria_weights["style_match"] * (1.0 if style else 0.7)
        return round(score, 4)

    def _generate_suggestions(self, scores: List[Dict[str, Any]]) -> List[str]:
        suggestions: List[str] = []
        for entry in scores:
            if entry["score"] < 0.7:
                aid = entry["candidate"].get("agent_id", "unknown")
                suggestions.append(f"Candidato {aid}: score bajo ({entry['score']}). Ampliar contenido.")
        return suggestions
