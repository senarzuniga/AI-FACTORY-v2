"""EPOCH protocol with round tracking, baselines, and rollback hooks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class OptimizationStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class EpochRound:
    round_id: int
    timestamp: datetime
    baseline_metrics: Dict[str, float]
    improvements: Dict[str, float]
    artifacts: List[str]
    status: OptimizationStatus
    rollback_plan: Optional[Dict[str, Any]] = None


class EpochProtocol:
    def __init__(self, config: Dict[str, Any], storage_path: Path):
        self.config = config
        self.storage_path = storage_path
        self.current_round = 0
        self.baseline: Optional[Dict[str, Any]] = None
        self.rounds: List[EpochRound] = []
        self.optimization_history: List[Dict[str, Any]] = []

        (storage_path / "epochs").mkdir(parents=True, exist_ok=True)
        (storage_path / "baselines").mkdir(parents=True, exist_ok=True)

    async def establish_baseline(self, system_metrics: Dict[str, float]) -> Dict[str, Any]:
        self.baseline = {
            "metrics": system_metrics,
            "threshold": self.config.get("baseline_threshold", 0.85),
            "established_at": datetime.now().isoformat(),
            "round_zero": self.current_round,
        }
        baseline_file = self.storage_path / "baselines" / f"baseline_round_{self.current_round}.json"
        baseline_file.write_text(json.dumps(self.baseline, indent=2), encoding="utf-8")
        return self.baseline

    async def start_optimization_round(self, hypothesis: Dict[str, Any]) -> int:
        if not self.baseline:
            raise RuntimeError("Baseline must be established before starting a round")

        self.current_round += 1
        round_data = EpochRound(
            round_id=self.current_round,
            timestamp=datetime.now(),
            baseline_metrics=dict(self.baseline["metrics"]),
            improvements={},
            artifacts=[],
            status=OptimizationStatus.PENDING,
        )
        self.rounds.append(round_data)

        round_dir = self.storage_path / "epochs" / f"round_{self.current_round}"
        round_dir.mkdir(parents=True, exist_ok=True)

        hypothesis_file = round_dir / "hypothesis.json"
        hypothesis_file.write_text(json.dumps(hypothesis, indent=2), encoding="utf-8")
        round_data.artifacts.append(str(hypothesis_file))
        round_data.status = OptimizationStatus.ACTIVE
        return self.current_round

    async def record_improvement(self, round_id: int, metric_name: str, old_value: float, new_value: float) -> bool:
        round_data = self._get_round(round_id)
        if not round_data or not self.baseline:
            return False

        improvement = (new_value - old_value) / old_value if old_value > 0 else 0.0
        round_data.improvements[metric_name] = improvement

        baseline_value = round_data.baseline_metrics.get(metric_name, old_value)
        normalized_gain = (new_value - baseline_value) / baseline_value if baseline_value > 0 else 0.0
        exceeds_threshold = normalized_gain >= float(self.baseline["threshold"])

        if exceeds_threshold:
            await self._commit_improvement(round_id, metric_name, new_value)
        return exceeds_threshold

    async def complete_round(self, round_id: int, final_metrics: Dict[str, float]) -> bool:
        round_data = self._get_round(round_id)
        if not round_data:
            return False

        performance_delta: Dict[str, float] = {}
        for metric, final_value in final_metrics.items():
            baseline_value = round_data.baseline_metrics.get(metric, final_value)
            performance_delta[metric] = (final_value - baseline_value) / baseline_value if baseline_value > 0 else 0.0

        regressed = any(delta < -0.1 for delta in performance_delta.values())
        if regressed and self.config.get("auto_rollback", True):
            await self._rollback_round(round_id)
            round_data.status = OptimizationStatus.ROLLED_BACK
            return False

        round_data.status = OptimizationStatus.COMPLETED
        report = {
            "round_id": round_id,
            "started_at": round_data.timestamp.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "baseline": round_data.baseline_metrics,
            "final": final_metrics,
            "improvements": round_data.improvements,
            "performance_delta": performance_delta,
            "status": round_data.status.value,
        }
        report_file = self.storage_path / "epochs" / f"round_{round_id}" / "final_report.json"
        report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        self.optimization_history.append(report)
        return not regressed

    async def _rollback_round(self, round_id: int) -> None:
        round_data = self._get_round(round_id)
        if not round_data:
            return

        if round_data.rollback_plan:
            for action in round_data.rollback_plan.get("actions", []):
                await self._execute_rollback_action(action)

        rollback_log = {
            "round_id": round_id,
            "rolled_back_at": datetime.now().isoformat(),
            "rollback_plan": round_data.rollback_plan,
            "reason": "Performance regression detected",
        }
        log_file = self.storage_path / "epochs" / f"round_{round_id}" / "rollback.json"
        log_file.write_text(json.dumps(rollback_log, indent=2), encoding="utf-8")

    async def _commit_improvement(self, round_id: int, metric_name: str, value: float) -> None:
        commit_file = self.storage_path / "epochs" / f"round_{round_id}" / "improvements.json"
        improvements: Dict[str, Any] = {}
        if commit_file.exists():
            improvements = json.loads(commit_file.read_text(encoding="utf-8"))

        improvements[metric_name] = {
            "value": value,
            "committed_at": datetime.now().isoformat(),
        }
        commit_file.write_text(json.dumps(improvements, indent=2), encoding="utf-8")

    def _get_round(self, round_id: int) -> Optional[EpochRound]:
        for item in self.rounds:
            if item.round_id == round_id:
                return item
        return None

    async def _execute_rollback_action(self, action: Dict[str, Any]) -> None:
        _ = action
        return
