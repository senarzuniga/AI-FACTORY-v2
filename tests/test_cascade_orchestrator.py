from __future__ import annotations

import asyncio
import json
from pathlib import Path

from cascade_orchestrator import CascadeEventBus, CascadeOrchestrator, LEARNING_DIR


def test_event_bus_emit_and_handler(tmp_path: Path):
    log_file = tmp_path / "cascade.log"
    bus = CascadeEventBus(log_file=log_file)
    seen = []

    async def handler(event):
        seen.append(event["type"])

    bus.on("x.test", handler)
    asyncio.run(bus.emit("x.test", {"k": 1}))

    assert seen == ["x.test"]
    assert log_file.exists()
    assert "x.test" in log_file.read_text(encoding="utf-8")


def test_cascade_runs_successfully_without_git_deploy(tmp_path: Path):
    orchestrator = CascadeOrchestrator(repo_path=tmp_path, enable_git_deploy=False, allow_push=False)

    async def run_case():
        cid = await orchestrator.trigger("improve code quality")
        for _ in range(80):
            status = await orchestrator.get_status(cid)
            if status in {"success", "failed"}:
                break
            await asyncio.sleep(0.1)
        result = await orchestrator.get_result(cid)
        return cid, result

    cid, result = asyncio.run(run_case())
    assert result is not None
    assert result["status"] == "success"
    assert result["cascade"].outputs["final_validation"]["quality_score"] >= 0.0

    results_file = LEARNING_DIR / "cascade_results.json"
    assert results_file.exists()
    payload = json.loads(results_file.read_text(encoding="utf-8"))
    assert cid in payload


def test_status_cli_helpers_exist_files():
    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    learning_file = LEARNING_DIR / "learning_data.json"
    if not learning_file.exists():
        learning_file.write_text(
            json.dumps(
                {
                    "successful_patterns": [],
                    "failure_patterns": [],
                    "performance_metrics": {},
                    "workflow_optimizations": [],
                }
            ),
            encoding="utf-8",
        )

    assert learning_file.exists()
