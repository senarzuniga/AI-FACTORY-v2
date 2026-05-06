"""
MEMORY AGENT
Guarda historico por cliente, decisiones previas, outputs relevantes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class MemoryAgent:
    """Persiste y recupera memoria por cliente."""

    def __init__(self, memory_path: str = "./memory/client_memories") -> None:
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)

    async def store(self, context: Dict[str, Any], output: Dict[str, Any]) -> None:
        client = context.get("client", "unknown")
        memory_file = self.memory_path / f"{client}_memory.json"

        memory: list = []
        if memory_file.exists():
            with open(memory_file, encoding="utf-8") as f:
                memory = json.load(f)

        memory.append(
            {
                "timestamp": datetime.now().isoformat(),
                "session_id": context.get("session_id"),
                "user": context.get("user_id"),
                "output_type": output.get("type"),
                "output_summary": str(output.get("content", ""))[:200],
                "metadata": output.get("metadata", {}),
            }
        )

        if len(memory) > 1000:
            memory = memory[-1000:]

        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

    async def load(self, context: Dict[str, Any], limit: int = 10) -> Dict[str, Any]:
        client = context.get("client", "unknown")
        memory_file = self.memory_path / f"{client}_memory.json"

        if not memory_file.exists():
            return {"history": [], "count": 0}

        with open(memory_file, encoding="utf-8") as f:
            memory = json.load(f)

        return {"history": memory[-limit:], "count": len(memory)}
