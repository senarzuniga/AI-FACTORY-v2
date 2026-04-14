"""
AI Factory v2 — Learning Registry

Records cycle outcomes so that the system can improve over time.
Data is persisted in a JSON file committed back to the repository.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from models.hypothesis import CycleResult
from utils.logger import get_logger

logger = get_logger(__name__)


class LearningRegistry:
    """Reads and writes learning history to a JSON file."""

    def __init__(self, history_path: str = "ai-factory-v2/learning/history.json") -> None:
        self.history_path = Path(history_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record(self, result: CycleResult) -> dict:
        """Append the outcome of a cycle to the history file and return the entry."""
        history = self._load()
        entry = self._build_entry(result)
        history.append(entry)
        self._save(history)
        logger.info(
            "Learning recorded — cycle %s | PR: %s | rejected: %s",
            result.cycle_id,
            result.pr_url or "none",
            result.rejected,
        )
        return entry

    def load_history(self) -> list[dict]:
        return self._load()

    def summary(self) -> dict:
        """Return high-level stats about past cycles."""
        history = self._load()
        total = len(history)
        executed = sum(1 for e in history if not e.get("rejected"))
        rejected = total - executed
        return {
            "total_cycles": total,
            "executed": executed,
            "rejected": rejected,
            "success_rate": round(executed / total, 2) if total else 0.0,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_entry(self, result: CycleResult) -> dict:
        entry: dict = {
            "cycle_id": result.cycle_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repository": result.repository,
            "problems_detected": len(result.problems),
            "hypotheses_generated": len(result.hypotheses),
            "rejected": result.rejected,
            "rejection_reason": result.rejection_reason,
            "pr_url": result.pr_url,
            "pr_number": result.pr_number,
        }
        if result.selected_hypothesis:
            h = result.selected_hypothesis
            entry["selected_hypothesis"] = {
                "id": h.id,
                "title": h.title,
                "approach": h.approach,
                "score": h.score.to_dict() if h.score else None,
            }
        return entry

    def _load(self) -> list[dict]:
        if not self.history_path.exists():
            return []
        try:
            text = self.history_path.read_text(encoding="utf-8").strip()
            if not text:
                return []
            return json.loads(text)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load learning history: %s", exc)
            return []

    def _save(self, history: list[dict]) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(
            json.dumps(history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
