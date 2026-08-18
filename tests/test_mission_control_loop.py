from cognitive_os.governance import Governance
from cognitive_os.mission_core import MissionManagerCore
from cognitive_os.models import EvidenceRecord, Hypothesis, MissionGap, MissionNode, QualityGate
from cognitive_os.registries import MissionGraph, MissionRegistry
from cognitive_os.runtimes import HypothesisEngine, ScoringEngine, ValidationEngine
from cognitive_os.system import CognitiveOperatingSystem


def build_core():
    graph = MissionGraph()
    hypotheses = HypothesisEngine()
    registry = MissionRegistry()
    core = MissionManagerCore(
        mission_graph=graph,
        hypothesis_engine=hypotheses,
        scoring_engine=ScoringEngine(),
        validation_engine=ValidationEngine(),
        governance=Governance(),
        mission_registry=registry,
    )
    return core, hypotheses, registry


def test_validated_hypothesis_does_not_complete_mission_with_executable_work():
    core, hypotheses, registry = build_core()
    mission = MissionNode(
        id="M-AUTONOMOUS",
        title="Autonomous ecosystem orchestration",
        objective="Close all governed mission gaps",
        gaps=[MissionGap(id="G-REGISTRY", statement="Consolidate capability registry", priority=5)],
        quality_gates=[QualityGate(id="Q-EVIDENCE", description="Evidence runtime contract passes")],
    )
    core.upsert_mission(mission)
    core.activate_unblocked()
    hypotheses.submit(
        Hypothesis(
            id="H-FOUNDATION",
            mission_id=mission.id,
            statement="Extend the canonical mission model",
            expected_value=0.9,
            implementation_plan=["model", "test", "validate"],
        )
    )

    result = core.evaluate_mission_hypotheses(mission.id)

    assert result.validated is True
    assert result.mission_complete is False
    assert registry.get(mission.id).mission_state == "continuation_required"
    assert {action["gap_id"] for action in result.next_actions} >= {"G-REGISTRY"}
    assert any("quality gate" in action["description"] for action in result.next_actions)


def test_mission_completes_only_after_gaps_and_quality_gates_close():
    core, hypotheses, registry = build_core()
    mission = MissionNode(
        id="M-READY",
        title="Ready mission",
        objective="Demonstrate completion readiness",
        evidence_ids=["EV-1"],
        gaps=[MissionGap(id="G-1", statement="Resolved gap", status="closed")],
        quality_gates=[QualityGate(id="Q-1", description="Validated evidence", evidence_ids=["EV-1"])],
    )
    core.upsert_mission(mission)
    core.activate_unblocked()
    hypotheses.submit(
        Hypothesis(
            id="H-READY",
            mission_id=mission.id,
            statement="Apply validated capability",
            expected_value=0.9,
            implementation_plan=["execute", "verify"],
        )
    )

    result = core.evaluate_mission_hypotheses(mission.id)

    assert result.validated is True
    assert result.mission_complete is True
    assert result.next_actions == []
    assert registry.get(mission.id).mission_state == "completed"


def test_mission_specific_weights_select_global_value_not_only_technical_quality():
    core, hypotheses, _ = build_core()
    mission = MissionNode(
        id="M-WEIGHTED",
        title="Business weighted mission",
        objective="Select global mission value",
        scoring_weights={"business_value": 20.0, "mission_alignment": 10.0, "architecture": 0.1},
    )
    core.upsert_mission(mission)
    core.activate_unblocked()
    hypotheses.submit(
        Hypothesis(
            id="H-TECHNICAL",
            mission_id=mission.id,
            statement="Technically elegant option",
            expected_value=0.72,
            metrics={"business_value": 0.2, "mission_alignment": 0.4, "architecture": 1.0},
        )
    )
    hypotheses.submit(
        Hypothesis(
            id="H-MISSION",
            mission_id=mission.id,
            statement="Mission-value option",
            expected_value=0.72,
            metrics={"business_value": 0.95, "mission_alignment": 0.95, "architecture": 0.6},
        )
    )

    result = core.evaluate_mission_hypotheses(mission.id)

    assert result.selected_hypothesis_id == "H-MISSION"
    assert (scorecard := core.snapshot()["missions"][0]["executive_scorecard"])
    assert scorecard["business_value"] == 0.95


def test_mission_control_explains_current_and_next_work(tmp_path):
    system = CognitiveOperatingSystem(memory_file=str(tmp_path / "memory.json"))
    mission = MissionNode(
        id="M-OBSERVE",
        title="Observable mission",
        objective="Explain autonomous work",
        gaps=[MissionGap(id="G-HIGH", statement="Integrate evidence runtime", priority=5)],
    )
    system.mission_core.upsert_mission(mission)
    system.mission_core.activate_unblocked()
    system.mission_core.evaluate_mission_hypotheses(mission.id)

    status = system.mission_control_status()

    assert status["no_idle"] is True
    assert status["what_will_it_do_next"]["gap_id"] == "G-HIGH"
    assert "Integrate evidence runtime" in status["why_working_on_this"]