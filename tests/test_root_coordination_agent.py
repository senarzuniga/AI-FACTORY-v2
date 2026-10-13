from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "agents" / "root_coordination_agent.py"


def load_agent():
    spec = importlib.util.spec_from_file_location("root_coordination_compat", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.RootCoordinationAgent


def test_direct_entrypoint_works_outside_repo(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--mission" in result.stdout


def test_default_root_and_governance() -> None:
    from root_coordination_agent import RootCoordinationAgent

    assert load_agent() is RootCoordinationAgent
    agent = load_agent()()
    assert agent.repo_root == ROOT
    assert agent.validate_governance()["governance_ready"] is True
    assert agent.continuous_improvement.repository_path() == str(
        ROOT / "Architecture" / "ContinuousImprovement"
    )


def test_run_preserves_explicit_root_and_persists_evidence(tmp_path: Path) -> None:
    agent = load_agent()(repo_root=tmp_path)
    result = agent.run("Test mission", "Verify evidence", context={"risk": "high"})
    assert result["ecosystem"]["repo_root"] == str(tmp_path)
    assert result["governance"]["governance_ready"] is False
    assert result["action_plan"][2]["priority"] == "critical"
    history = tmp_path / "Architecture" / "ContinuousImprovement" / "05_PROGRESS_HISTORY.md"
    assert "Test mission" in history.read_text(encoding="utf-8")
