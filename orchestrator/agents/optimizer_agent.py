"""Optimizer agent for protocol-level tuning recommendations."""

from __future__ import annotations

from typing import Any, Dict


class OptimizerAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.learning_rate = float(config.get("learning_rate", 0.01))

    async def suggest_adjustments(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        current = float(metrics.get("overall_score", 0.5))
        pressure = max(0.0, min(1.0, 1.0 - current))
        return {
            "learning_rate": max(0.0001, self.learning_rate * (1.0 + pressure * 0.5)),
            "exploration_boost": pressure,
        }
