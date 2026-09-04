"""Knowledge Core APIs for reusable cross-platform consumption."""

from __future__ import annotations

from typing import Any

from cognitive_os.memory_core import EnterpriseMemoryCore
from cognitive_os.models import EvidenceRecord, TruthAssertion
from cognitive_os.runtimes import EvidenceRuntime, TruthRuntime


class KnowledgeCoreAPIs:
    def __init__(
        self,
        memory_core: EnterpriseMemoryCore,
        evidence_runtime: EvidenceRuntime,
        truth_runtime: TruthRuntime,
    ) -> None:
        self._memory_core = memory_core
        self._evidence_runtime = evidence_runtime
        self._truth_runtime = truth_runtime

    def put_knowledge(self, key: str, value: Any, namespace: str = "knowledge") -> None:
        self._memory_core.put(namespace, key, value)

    def get_knowledge(self, key: str, namespace: str = "knowledge") -> Any:
        return self._memory_core.get(namespace, key)

    def ingest_evidence(self, evidence: EvidenceRecord) -> None:
        self._evidence_runtime.add(evidence)

    def assert_truth(self, assertion: TruthAssertion) -> TruthAssertion:
        return self._truth_runtime.upsert(assertion)

    def export_snapshot(self) -> dict[str, Any]:
        return {
            "memory": self._memory_core.snapshot(),
            "evidence": [e.__dict__ for e in self._evidence_runtime.list()],
            "truth": [t.__dict__ for t in self._truth_runtime.list()],
        }
