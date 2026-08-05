from __future__ import annotations

from pathlib import Path

from cognitive_os.layout_versioning import LayoutVersionStore


def _sample_snapshot(layout_name: str, node_suffix: str) -> dict:
    return {
        "layout_name": layout_name,
        "factory_graph": {
            "nodes": [
                {"id": f"machine-{node_suffix}", "kind": "machine"},
                {"id": f"buffer-{node_suffix}", "kind": "buffer"},
            ],
            "edges": [
                {
                    "source": f"machine-{node_suffix}",
                    "target": f"buffer-{node_suffix}",
                    "relation": "queues_to",
                }
            ],
        },
    }


def test_layout_versioning_snapshot_compare_and_rollback(tmp_path: Path) -> None:
    store = LayoutVersionStore(persistence_file=str(tmp_path / "layout_versions.json"))

    rev1 = store.create_snapshot(
        layout_name="layout-A",
        source_hash="source-1",
        snapshot=_sample_snapshot("layout-A", "1"),
        scenario="baseline",
        branch="main",
        set_baseline=True,
    )
    rev2 = store.create_snapshot(
        layout_name="layout-A",
        source_hash="source-2",
        snapshot=_sample_snapshot("layout-A", "2"),
        scenario="alt",
        branch="feature-x",
        set_baseline=False,
    )

    history = store.list_history("layout-A")
    assert history["revision_count"] == 2

    diff = store.compare_revisions(
        layout_name="layout-A",
        revision_a=rev1["revision"]["revision_id"],
        revision_b=rev2["revision"]["revision_id"],
    )
    assert diff["node_delta"]["added"]
    assert diff["node_delta"]["removed"]

    rolled = store.rollback("layout-A", rev1["revision"]["revision_id"])
    assert rolled["rollback_to"] == rev1["revision"]["revision_id"]
