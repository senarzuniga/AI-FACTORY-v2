"""Autonomous execution framework for the Cognitive Operating System."""

from __future__ import annotations

from cognitive_os.mission_core import MissionManagerCore
from cognitive_os.models import ExecutionResult, MissionStatus


class AutonomousExecutionFramework:
    """
    Runs the workflow loop:
      Hypothesis -> Scoring -> Selection -> Validation
    and stops when no positive engineering action remains.
    """

    def __init__(self, mission_core: MissionManagerCore, positive_score_threshold: float = 0.65) -> None:
        self._mission_core = mission_core
        self._positive_score_threshold = positive_score_threshold

    def run_until_stable(self, max_cycles: int = 100) -> dict:
        cycle = 0
        results: list[dict] = []

        while cycle < max_cycles:
            cycle += 1
            self._mission_core.activate_unblocked()
            active_missions = [
                mission for mission in self._mission_core.list_missions() if mission.status == MissionStatus.ACTIVE
            ]

            if not active_missions:
                break

            positive_action_done = False
            for mission in active_missions:
                outcome: ExecutionResult = self._mission_core.evaluate_mission_hypotheses(mission.id)
                results.append(
                    {
                        "cycle": cycle,
                        "mission_id": mission.id,
                        "selected_hypothesis_id": outcome.selected_hypothesis_id,
                        "validated": outcome.validated,
                        "score": outcome.score,
                        "reason": outcome.reason,
                        "executed_steps": outcome.executed_steps,
                    }
                )

                if outcome.validated and outcome.score >= self._positive_score_threshold:
                    positive_action_done = True

            if not positive_action_done:
                break

        return {
            "status": "stable",
            "cycles_executed": cycle,
            "results": results,
            "snapshot": self._mission_core.snapshot(),
        }
