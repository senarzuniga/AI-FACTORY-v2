import json

from cognitive_os.ecosystem_discovery import EcosystemDiscovery
from cognitive_os.system import CognitiveOperatingSystem


def test_discovery_registers_available_repositories_agents_and_verified_capabilities(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    repo = workspace / "AI-FACTORY-v2"
    (repo / "agents").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "docs" / "aeos_review").mkdir(parents=True)
    (repo / "AGENTS.md").write_text("# Agent instructions", encoding="utf-8")
    (repo / "README.md").write_text("# AI Factory test repository", encoding="utf-8")
    (repo / "agents" / "planner_agent.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_runtime.py").write_text("", encoding="utf-8")
    (repo / "capability.py").write_text("", encoding="utf-8")
    (repo / "docs" / "aeos_review" / "Capability_Registry.json").write_text(
        json.dumps({"capabilities": [{"name": "Mission Management", "status": "partial", "evidence": ["capability.py"]}]}),
        encoding="utf-8",
    )

    system = CognitiveOperatingSystem(memory_file=str(tmp_path / "memory.json"))
    discovery = EcosystemDiscovery(system, workspace_parent=workspace)
    monkeypatch.setattr(discovery, "_repo_root", repo)
    summary = discovery.discover()

    assert summary["available_repositories"] == 1
    assert system.repository_registry.get("AI_FACTORY").purpose == "AI Factory test repository"
    assert any(agent.id.startswith("AI_FACTORY:") for agent in system.agent_registry.list())
    assert any(node.id == "mission-management" for node in system.capability_graph.list_nodes())
    assert system.knowledge_registry.list()[0].classification == "VALIDATED"
    assert system.evidence_runtime.get("evidence-ecosystem-discovery-latest") is not None
    mission = system.mission_registry.get("IMPROVE-AI-FACTORY")
    assert mission is not None
    assert mission.mission_state == "continuation_required"
    assert next(gate for gate in mission.quality_gates if gate.id == "Q-DISCOVERY").status == "passed"
    assert any(action.gap_id == "G-CROSS-REPOSITORY-CONTRACT" for action in mission.next_actions)