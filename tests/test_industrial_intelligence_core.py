from __future__ import annotations

from cognitive_os.system import CognitiveOperatingSystem


def test_m010_components_are_registered_and_dependency_ordered() -> None:
    system = CognitiveOperatingSystem()

    components = system.industrial_intelligence.list_components()
    component_ids = [item["id"] for item in components]

    assert len(components) == 14
    assert component_ids[0] == "industrial-geometry-engine"
    assert component_ids[-1] == "smart-proposal-intelligence-runtime"

    mission = system.mission_registry.get("M010")
    assert mission is not None
    assert mission.id == "M010"


def test_industrial_component_execution_generates_health_and_output() -> None:
    system = CognitiveOperatingSystem()
    result = system.industrial_intelligence.execute_component(
        "industrial-simulation-runtime",
        {"scenarios": ["baseline", "high-demand"]},
    )

    health = system.industrial_intelligence.health()

    assert result["status"] == "completed"
    assert result["scenario_count"] == 2
    assert health["status"] == "ok"


def test_ahde_decision_produces_ranked_hypotheses() -> None:
    system = CognitiveOperatingSystem()
    decision = system.industrial_intelligence.ahde_decide(
        mission_id="M010",
        uncertainty="factory flow uncertainty",
        context={"plant": "A", "line": "L1"},
    )

    assert decision["selected"] is not None
    assert len(decision["evaluated"]) >= 3
    assert decision["evaluated"][0]["score"] >= decision["evaluated"][-1]["score"]
