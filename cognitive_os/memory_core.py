"""Enterprise memory core with optional JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EnterpriseMemoryCore:
    def __init__(self, persistence_file: str | None = None) -> None:
        self._memory: dict[str, dict[str, Any]] = {}
        self._persistence_file = Path(persistence_file) if persistence_file else None
        if self._persistence_file and self._persistence_file.exists():
            self._memory = json.loads(self._persistence_file.read_text(encoding="utf-8"))

    def put(self, namespace: str, key: str, value: Any) -> None:
        self._memory.setdefault(namespace, {})[key] = value
        self._save()

    def get(self, namespace: str, key: str) -> Any:
        return self._memory.get(namespace, {}).get(key)

    def list_namespace(self, namespace: str) -> dict[str, Any]:
        return dict(self._memory.get(namespace, {}))

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {ns: dict(values) for ns, values in self._memory.items()}

    def _save(self) -> None:
        if not self._persistence_file:
            return
        self._persistence_file.parent.mkdir(parents=True, exist_ok=True)
        self._persistence_file.write_text(json.dumps(self._memory, indent=2), encoding="utf-8")
