"""Accelerated 7-hour autonomous simulation for cascade orchestrator robustness checks."""

from __future__ import annotations

import asyncio
import json
import random
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "data" / "simulation_7h_report.json"
sys.path.insert(0, str(ROOT))

from cascade_orchestrator import CascadeOrchestrator

TRIGGERS = [
    "improve code quality and resilience",
    "fix security validation edge cases",
    "add feature instrumentation for monitoring",
    "optimize performance and reduce latency",
    "stabilize retry logic and failure handling",
    "harden deployment safety checks",
    "synchronize linked applications",
]


async def run_simulation() -> int:
    random.seed(42)
    orchestrator = CascadeOrchestrator(repo_path=ROOT, enable_git_deploy=False, allow_push=False)

    start = datetime.now(UTC)
    virtual_minutes = 7 * 60
    failures: List[Dict[str, Any]] = []
    runs: List[Dict[str, Any]] = []

    for minute in range(virtual_minutes):
        trigger = random.choice(TRIGGERS)
        context: Dict[str, Any] = {
            "candidate_files": ["main.py", "cascade_orchestrator.py"],
            "constraints": {"virtual_minute": minute, "simulation_window_hours": 7},
            "enable_linked_deploy": minute % 60 == 0,
            "agent_timeout_seconds": 45,
        }

        cascade_id = await orchestrator.trigger(trigger, context=context)

        # Poll until completion.
        while True:
            status = await orchestrator.get_status(cascade_id)
            if status in {"success", "failed", "not_found"}:
                break
            await asyncio.sleep(0.01)

        result = await orchestrator.get_result(cascade_id)
        if not result:
            failures.append({"minute": minute, "cascade_id": cascade_id, "error": "missing_result"})
            continue

        cascade = result["cascade"]
        row = {
            "minute": minute,
            "cascade_id": cascade_id,
            "status": result["status"],
            "trigger": trigger,
            "duration_seconds": cascade.metrics.get("duration_seconds", 0.0),
            "quality": cascade.outputs.get("final_validation", {}).get("quality_score", 0.0),
            "deployments": len(cascade.deployed_features),
            "linked_deploy": context["enable_linked_deploy"],
            "errors": cascade.errors,
        }
        runs.append(row)

        if result["status"] != "success":
            failures.append({"minute": minute, "cascade_id": cascade_id, "error": result.get("error", "unknown")})
            # One immediate retry with safe trigger.
            retry_id = await orchestrator.trigger("stabilize retry logic and failure handling", context=context)
            while True:
                retry_status = await orchestrator.get_status(retry_id)
                if retry_status in {"success", "failed", "not_found"}:
                    break
                await asyncio.sleep(0.01)
            retry_result = await orchestrator.get_result(retry_id)
            if not retry_result or retry_result["status"] != "success":
                failures.append({"minute": minute, "cascade_id": retry_id, "error": "retry_failed"})

    elapsed = (datetime.now(UTC) - start).total_seconds()
    durations = [float(r["duration_seconds"]) for r in runs]
    qualities = [float(r["quality"]) for r in runs]

    report = {
        "started_at": start.isoformat(),
        "completed_at": datetime.now(UTC).isoformat(),
        "virtual_minutes_simulated": virtual_minutes,
        "total_runs": len(runs),
        "total_failures": len(failures),
        "average_duration_seconds": round(sum(durations) / max(len(durations), 1), 4),
        "max_duration_seconds": round(max(durations) if durations else 0.0, 4),
        "average_quality": round(sum(qualities) / max(len(qualities), 1), 4),
        "linked_deploy_runs": sum(1 for r in runs if r["linked_deploy"]),
        "wall_clock_seconds": round(elapsed, 2),
        "failures": failures,
        "sample_runs": runs[:10],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=" * 70)
    print("AUTONOMOUS 7H SIMULATION COMPLETE")
    print("=" * 70)
    print(f"virtual_minutes_simulated: {report['virtual_minutes_simulated']}")
    print(f"total_runs: {report['total_runs']}")
    print(f"total_failures: {report['total_failures']}")
    print(f"average_duration_seconds: {report['average_duration_seconds']}")
    print(f"average_quality: {report['average_quality']}")
    print(f"linked_deploy_runs: {report['linked_deploy_runs']}")
    print(f"report: {REPORT_PATH}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_simulation()))
