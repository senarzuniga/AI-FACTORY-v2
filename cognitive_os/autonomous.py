"""Autonomous execution framework for the Cognitive Operating System."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

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
        self._repo_root = Path(__file__).resolve().parents[1]
        self._layout_status_script = self._repo_root / "scripts" / "generate_layout_workbench_status.py"

    def _refresh_layout_status(self, cycle: int) -> dict:
        if not self._layout_status_script.exists():
            return {
                "cycle": cycle,
                "ok": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": f"status script missing: {self._layout_status_script}",
            }

        process = subprocess.run(
            [sys.executable, str(self._layout_status_script)],
            cwd=str(self._repo_root),
            check=False,
            capture_output=True,
            text=True,
        )
        return {
            "cycle": cycle,
            "ok": process.returncode == 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "returncode": process.returncode,
            "stdout": process.stdout.strip(),
            "stderr": process.stderr.strip(),
        }

    def run_until_stable(self, max_cycles: int = 100) -> dict:
        cycle = 0
        results: list[dict] = []
        layout_status_refreshes: list[dict] = []

        while cycle < max_cycles:
            cycle += 1
            self._mission_core.activate_unblocked()
            active_missions = [
                mission for mission in self._mission_core.list_missions() if mission.status == MissionStatus.ACTIVE
            ]

            if not active_missions:
                layout_status_refreshes.append(self._refresh_layout_status(cycle))
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
                        "mission_complete": outcome.mission_complete,
                        "next_actions": outcome.next_actions,
                    }
                )

                if outcome.validated and outcome.score >= self._positive_score_threshold:
                    positive_action_done = True

            layout_status_refreshes.append(self._refresh_layout_status(cycle))

            if not positive_action_done:
                break

        return {
            "status": "stable",
            "cycles_executed": cycle,
            "results": results,
            "layout_status_refreshes": layout_status_refreshes,
            "snapshot": self._mission_core.snapshot(),
        }
