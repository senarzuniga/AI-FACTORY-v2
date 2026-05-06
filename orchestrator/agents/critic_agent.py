"""Critic agent for safety and quality validation gates."""

from __future__ import annotations

from typing import Any, Dict, List


class CriticAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validators = config.get("enabled_validators", ["security", "performance", "maintainability", "scalability"])

    async def validate(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        risks: List[str] = []
        score = 0.75

        text = " ".join(
            [
                str(hypothesis.get("title", "")),
                str(hypothesis.get("description", "")),
                str(hypothesis.get("approach", "")),
            ]
        ).lower()

        if "rewrite" in text or "migrate all" in text:
            risks.append("Plan may be too large or disruptive.")
            score -= 0.25
        if "skip tests" in text:
            risks.append("Plan weakens validation safety.")
            score -= 0.35

        status = "approved" if score >= 0.6 else "rejected"
        return {
            "status": status,
            "score": max(0.0, min(1.0, score)),
            "risks": risks,
            "validators": self.validators,
            "feedback": "Approved for execution" if status == "approved" else "Blocked by critic safety gates",
        }
