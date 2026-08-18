"""Registries and graph primitives for reusable Cognitive OS services."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict

from cognitive_os.models import AgentProfile, CapabilityNode, KnowledgeNode, MissionNode, PlatformConsumer, RepositoryNode


class AICoordinator:
    """Coordinates service-level interactions across registered components."""

    def __init__(self) -> None:
        self._events: list[dict] = []

    def publish(self, event_type: str, payload: dict) -> None:
        self._events.append({"event_type": event_type, "payload": payload})

    def recent_events(self, limit: int = 100) -> list[dict]:
        return self._events[-limit:]


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentProfile] = {}

    def register(self, agent: AgentProfile) -> None:
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> AgentProfile | None:
        return self._agents.get(agent_id)

    def list(self) -> list[AgentProfile]:
        return list(self._agents.values())


class PlatformRegistry:
    def __init__(self) -> None:
        self._platforms: dict[str, PlatformConsumer] = {}
        self._contract_version = "mission-model-v1"

    def register(self, platform: PlatformConsumer) -> None:
        self._platforms[platform.id] = platform

    def list(self) -> list[PlatformConsumer]:
        return list(self._platforms.values())

    def contract_version(self) -> str:
        return self._contract_version


class RepositoryRegistry:
    def __init__(self) -> None:
        self._repositories: dict[str, RepositoryNode] = {}

    def upsert(self, repository: RepositoryNode) -> None:
        self._repositories[repository.id] = repository

    def get(self, repository_id: str) -> RepositoryNode | None:
        return self._repositories.get(repository_id)

    def list(self) -> list[RepositoryNode]:
        return list(self._repositories.values())


class KnowledgeRegistry:
    def __init__(self) -> None:
        self._knowledge: dict[str, KnowledgeNode] = {}

    def upsert(self, knowledge: KnowledgeNode) -> None:
        self._knowledge[knowledge.id] = knowledge

    def list(self) -> list[KnowledgeNode]:
        return list(self._knowledge.values())


class CapabilityGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, CapabilityNode] = {}
        self._edges: dict[str, set[str]] = defaultdict(set)
        self._schema_version = "mission-model-v1"

    def upsert_node(self, node: CapabilityNode) -> None:
        self._nodes[node.id] = node
        for dep in node.dependencies:
            self._edges[node.id].add(dep)

    def list_nodes(self) -> list[CapabilityNode]:
        return list(self._nodes.values())

    def dependencies_of(self, capability_id: str) -> list[str]:
        return sorted(self._edges.get(capability_id, set()))

    def schema_version(self) -> str:
        return self._schema_version


class MissionRegistry:
    """Canonical mission registry acting as the source of truth for mission records."""

    def __init__(self) -> None:
        self._missions: dict[str, MissionNode] = {}
        self._schema_version = "mission-model-v1"

    def upsert(self, mission: MissionNode) -> None:
        self._missions[mission.id] = mission

    def get(self, mission_id: str) -> MissionNode | None:
        return self._missions.get(mission_id)

    def list(self) -> list[MissionNode]:
        return list(self._missions.values())

    def snapshot(self) -> dict:
        return {
            "schema_version": self._schema_version,
            "missions": [asdict(mission) for mission in self._missions.values()],
        }

    def schema_version(self) -> str:
        return self._schema_version


class MissionGraph:
    def __init__(self) -> None:
        self._missions: dict[str, MissionNode] = {}
        self._edges: dict[str, set[str]] = defaultdict(set)

    def upsert(self, mission: MissionNode) -> None:
        self._missions[mission.id] = mission
        self._edges[mission.id] = set(mission.dependencies)

    def get(self, mission_id: str) -> MissionNode | None:
        return self._missions.get(mission_id)

    def list(self) -> list[MissionNode]:
        return list(self._missions.values())

    def is_unblocked(self, mission_id: str) -> bool:
        deps = self._edges.get(mission_id, set())
        for dep in deps:
            mission = self._missions.get(dep)
            if not mission or mission.status.value != "completed":
                return False
        return True
