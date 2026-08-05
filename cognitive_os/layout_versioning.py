"""Persistent layout snapshot and revision management."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_payload(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]


@dataclass(slots=True)
class LayoutRevision:
    revision_id: str
    layout_name: str
    branch: str
    scenario: str
    revision_note: str
    parent_revision_id: str | None
    created_at: str
    source_hash: str
    snapshot_hash: str


class LayoutVersionStore:
    def __init__(self, persistence_file: str | None = None) -> None:
        self._file = Path(persistence_file or "data/layout_versions.json")
        self._db = self._load()

    def create_snapshot(
        self,
        layout_name: str,
        source_hash: str,
        snapshot: dict[str, Any],
        scenario: str = "baseline",
        revision_note: str = "",
        branch: str = "main",
        parent_revision_id: str | None = None,
        set_baseline: bool = False,
    ) -> dict[str, Any]:
        if not parent_revision_id:
            parent_revision_id = self._latest_revision_id(layout_name, branch)

        snap_hash = _hash_payload(snapshot)
        revision_id = f"rev-{layout_name.lower().replace(' ', '-')}-{snap_hash[:8]}"
        revision = LayoutRevision(
            revision_id=revision_id,
            layout_name=layout_name,
            branch=branch,
            scenario=scenario,
            revision_note=revision_note or "automated snapshot",
            parent_revision_id=parent_revision_id,
            created_at=_now(),
            source_hash=source_hash,
            snapshot_hash=snap_hash,
        )

        self._db.setdefault("layouts", {}).setdefault(layout_name, {"revisions": [], "baseline_revision_id": None})
        layout_state = self._db["layouts"][layout_name]
        layout_state["revisions"].append({
            "meta": asdict(revision),
            "snapshot": snapshot,
        })
        if set_baseline or not layout_state.get("baseline_revision_id"):
            layout_state["baseline_revision_id"] = revision.revision_id

        self._save()
        return {
            "revision": asdict(revision),
            "baseline_revision_id": layout_state.get("baseline_revision_id"),
        }

    def set_baseline(self, layout_name: str, revision_id: str) -> dict[str, Any]:
        layout_state = self._db.get("layouts", {}).get(layout_name)
        if not layout_state:
            raise ValueError(f"unknown layout '{layout_name}'")
        if revision_id not in {item["meta"]["revision_id"] for item in layout_state.get("revisions", [])}:
            raise ValueError(f"unknown revision '{revision_id}' for layout '{layout_name}'")
        layout_state["baseline_revision_id"] = revision_id
        self._save()
        return {
            "layout_name": layout_name,
            "baseline_revision_id": revision_id,
        }

    def rollback(self, layout_name: str, revision_id: str) -> dict[str, Any]:
        snapshot = self.get_snapshot(layout_name, revision_id)
        self.set_baseline(layout_name, revision_id)
        return {
            "layout_name": layout_name,
            "rollback_to": revision_id,
            "snapshot": snapshot,
        }

    def get_snapshot(self, layout_name: str, revision_id: str) -> dict[str, Any]:
        for item in self._db.get("layouts", {}).get(layout_name, {}).get("revisions", []):
            if item["meta"]["revision_id"] == revision_id:
                return item["snapshot"]
        raise ValueError(f"snapshot not found: {layout_name}/{revision_id}")

    def list_history(self, layout_name: str) -> dict[str, Any]:
        layout_state = self._db.get("layouts", {}).get(layout_name, {})
        revisions = [item["meta"] for item in layout_state.get("revisions", [])]
        return {
            "layout_name": layout_name,
            "baseline_revision_id": layout_state.get("baseline_revision_id"),
            "revision_count": len(revisions),
            "revisions": revisions,
        }

    def compare_revisions(self, layout_name: str, revision_a: str, revision_b: str) -> dict[str, Any]:
        snap_a = self.get_snapshot(layout_name, revision_a)
        snap_b = self.get_snapshot(layout_name, revision_b)

        nodes_a = {node.get("id") for node in snap_a.get("factory_graph", {}).get("nodes", [])}
        nodes_b = {node.get("id") for node in snap_b.get("factory_graph", {}).get("nodes", [])}
        edges_a = {
            (edge.get("source"), edge.get("target"), edge.get("relation"))
            for edge in snap_a.get("factory_graph", {}).get("edges", [])
        }
        edges_b = {
            (edge.get("source"), edge.get("target"), edge.get("relation"))
            for edge in snap_b.get("factory_graph", {}).get("edges", [])
        }

        return {
            "layout_name": layout_name,
            "revision_a": revision_a,
            "revision_b": revision_b,
            "node_delta": {
                "added": sorted(nodes_b - nodes_a),
                "removed": sorted(nodes_a - nodes_b),
                "unchanged": len(nodes_a & nodes_b),
            },
            "edge_delta": {
                "added": sorted(list(edges_b - edges_a)),
                "removed": sorted(list(edges_a - edges_b)),
                "unchanged": len(edges_a & edges_b),
            },
            "snapshot_hash": {
                "a": _hash_payload(snap_a),
                "b": _hash_payload(snap_b),
            },
        }

    def compare_branches(self, layout_name: str, branch_a: str, branch_b: str) -> dict[str, Any]:
        rev_a = self._latest_revision_id(layout_name, branch_a)
        rev_b = self._latest_revision_id(layout_name, branch_b)
        if not rev_a or not rev_b:
            raise ValueError("branch comparison requires revisions in both branches")
        return self.compare_revisions(layout_name, rev_a, rev_b)

    def _latest_revision_id(self, layout_name: str, branch: str) -> str | None:
        revisions = self._db.get("layouts", {}).get(layout_name, {}).get("revisions", [])
        for item in reversed(revisions):
            if item["meta"].get("branch") == branch:
                return str(item["meta"]["revision_id"])
        return None

    def _load(self) -> dict[str, Any]:
        if self._file.exists():
            return json.loads(self._file.read_text(encoding="utf-8"))
        return {"layouts": {}}

    def _save(self) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text(json.dumps(self._db, indent=2), encoding="utf-8")
