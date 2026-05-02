"""Co-EPG trainer for planning-grounding co-evolution feedback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CoEPGState:
    planning_score: float = 0.5
    grounding_score: float = 0.5
    reward: float = 0.0
    updates: int = 0


class CoEPGTrainer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.planning_weight = float(config.get("planning_weight", 0.4))
        self.grounding_weight = float(config.get("grounding_weight", 0.6))
        self.reward_decay = float(config.get("reward_decay", 0.95))
        self.state = CoEPGState()

    def update(self, planning_success: float, grounding_success: float, critic_score: float) -> Dict[str, float]:
        planning_success = float(max(0.0, min(1.0, planning_success)))
        grounding_success = float(max(0.0, min(1.0, grounding_success)))
        critic_score = float(max(0.0, min(1.0, critic_score)))

        combined = (
            self.planning_weight * planning_success
            + self.grounding_weight * grounding_success
            + 0.25 * critic_score
        )

        self.state.reward = self.state.reward * self.reward_decay + combined * (1 - self.reward_decay)
        self.state.planning_score = self.state.planning_score * 0.8 + planning_success * 0.2
        self.state.grounding_score = self.state.grounding_score * 0.8 + grounding_success * 0.2
        self.state.updates += 1

        return {
            "reward": self.state.reward,
            "planning_score": self.state.planning_score,
            "grounding_score": self.state.grounding_score,
            "updates": float(self.state.updates),
        }
