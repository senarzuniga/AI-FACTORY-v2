from __future__ import annotations

from pathlib import Path

from cognitive_os.continuous_improvement import ContinuousImprovementRepository


def test_continuous_improvement_repository_generates_governance_docs(tmp_path: Path) -> None:
    repo = ContinuousImprovementRepository(root_dir=str(tmp_path / "Architecture" / "ContinuousImprovement"))
    repo.ensure_repository()

    state = {
        "platforms": [{"id": "industrial-layout-workbench"}],
        "capabilities": [{"id": "layout-analysis-workbench"}],
        "mission_registry": {"missions": [{"id": "M013"}]},
        "knowledge": {
            "evidence": [{"id": "e-1"}],
            "truth": [{"id": "t-1"}],
        },
    }
    result = repo.refresh(
        state=state,
        mission_event={
            "mission_id": "M013",
            "event": "test-refresh",
            "agents": ["AI Coordinator"],
        },
    )

    root = Path(result["repository"])
    assert (root / "01_OBJECTIVES.md").exists()
    assert (root / "02_CURRENT_STATE.md").exists()
    assert (root / "03_GAP_ANALYSIS.md").exists()
    assert (root / "04_EXECUTION_BACKLOG.md").exists()
    assert (root / "05_PROGRESS_HISTORY.md").exists()
    assert result["idle_permitted"] in {True, False}
