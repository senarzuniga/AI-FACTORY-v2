"""Lossless migration of legacy mission artifacts to canonical mission model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MISSION_PORTFOLIO_DIR = ROOT / "mission_portfolio"
AEOS_GRAPH_FILE = ROOT / "docs" / "aeos_review" / "Mission_Graph.json"
OUTPUT_DIR = ROOT / "data" / "missions"
CANONICAL_OUTPUT_FILE = OUTPUT_DIR / "canonical_missions_v1.json"
LEGACY_ARCHIVE_FILE = OUTPUT_DIR / "canonical_missions_legacy_archive.json"
MIGRATION_REPORT_FILE = OUTPUT_DIR / "canonical_mission_migration_report.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_value(raw: float | int | None) -> float:
    if raw is None:
        return 0.0
    value = float(raw)
    if value > 1.0:
        return max(0.0, min(1.0, value / 100.0))
    return max(0.0, min(1.0, value))


def migrate() -> dict[str, Any]:
    portfolio_files = sorted(MISSION_PORTFOLIO_DIR.glob("mission_portfolio_*.json"))
    portfolios = [read_json(path) for path in portfolio_files]
    graph_data = read_json(AEOS_GRAPH_FILE) if AEOS_GRAPH_FILE.exists() else {"nodes": [], "edges": []}

    node_map = {node.get("id"): node for node in graph_data.get("nodes", [])}
    edges = graph_data.get("edges", [])

    canonical: dict[str, dict[str, Any]] = {}
    legacy_archive: dict[str, list[dict[str, Any]]] = {}

    for portfolio in portfolios:
        candidates = portfolio.get("candidates", [])
        missions = portfolio.get("missions", [])

        # Portfolio 001 style
        for candidate in candidates:
            mission_id = candidate.get("mission_id")
            if not mission_id:
                continue
            normalized = candidate.get("normalized_metrics", {})
            record = canonical.setdefault(mission_id, _empty_canonical_mission(mission_id, candidate.get("title", mission_id)))
            record["objective"] = candidate.get("description", record["objective"])
            record["objectives"] = [{"id": f"{mission_id}-OBJ-1", "statement": record["objective"], "owner": "Executive Engineering Board", "priority": 1}]
            record["value"] = {
                "business_value": normalize_value(normalized.get("business_value", 0.0)),
                "engineering_value": normalize_value(normalized.get("engineering_value", 0.0)),
                "knowledge_value": normalize_value(normalized.get("knowledge_reuse", 0.0)),
            }
            record["dependencies"] = list(dict.fromkeys(candidate.get("dependencies", [])))
            record["mission_score"] = normalize_value(candidate.get("global_score_norm", 0.0))
            record["mission_roi"] = normalize_value(normalized.get("expected_roi", 0.0))
            record["mission_confidence"] = normalize_value(normalized.get("implementation_risk_score", 0.0))
            record["mission_traceability"]["source_documents"].append("mission_portfolio_001.json")
            legacy_archive.setdefault(mission_id, []).append({"source": portfolio.get("portfolio_id"), "payload": candidate})

        # Portfolio 003 style
        for mission in missions:
            mission_id = mission.get("id")
            if not mission_id:
                continue
            record = canonical.setdefault(mission_id, _empty_canonical_mission(mission_id, node_map.get(mission_id, {}).get("title", mission_id)))
            record["mission_state"] = mission.get("status", record["mission_state"])
            record["work_packages"] = [
                {
                    "id": package.get("id", ""),
                    "title": package.get("name", ""),
                    "status": package.get("path_type", "planned"),
                    "owner": "",
                    "depends_on": mission.get("mandatory_dependencies", []),
                    "deliverables": [package.get("type", "")],
                }
                for package in mission.get("work_packages", [])
            ]
            record["deliverables"] = [package.get("name", "") for package in mission.get("work_packages", [])]
            record["capabilities"] = mission.get("reusable_assets", [])
            record["milestones"].append(
                {
                    "id": f"{mission_id}-M1",
                    "name": "Migrated from legacy portfolio",
                    "due_at": "2026-12-31T00:00:00Z",
                    "status": "planned",
                }
            )
            record["mission_traceability"]["source_documents"].append("mission_portfolio_003_parallel_30d.json")
            legacy_archive.setdefault(mission_id, []).append({"source": portfolio.get("portfolio_id"), "payload": mission})

    for mission_id, record in canonical.items():
        edge_dependencies = [edge["from"] for edge in edges if edge.get("to") == mission_id]
        record["dependencies"] = list(dict.fromkeys(record["dependencies"] + edge_dependencies))
        record["mission_traceability"]["dependency_links"] = record["dependencies"]
        record["mission_knowledge_assets"].append(
            {
                "id": f"{mission_id}-KNOW-LEGACY",
                "asset_type": "legacy_archive",
                "uri": f"canonical_missions_legacy_archive.json#{mission_id}",
                "description": "Lossless legacy source payload archive",
            }
        )
        record["mission_history"].append(
            {
                "timestamp": "2026-07-24T00:00:00Z",
                "event_type": "migrated",
                "detail": "Migrated from legacy mission artifacts into canonical mission model",
                "actor": "migration-script",
            }
        )
        record["mission_evolution"].append(
            {
                "version": 1,
                "change_summary": "Initial canonical model migration",
                "changed_at": "2026-07-24T00:00:00Z",
            }
        )

    payload = {
        "schema": "mission-model-v1",
        "migrated_at": "2026-07-24T00:00:00Z",
        "missions": sorted(canonical.values(), key=lambda item: item["id"]),
    }

    report = {
        "status": "completed",
        "missions_migrated": len(payload["missions"]),
        "sources": [path.name for path in portfolio_files] + ([AEOS_GRAPH_FILE.name] if AEOS_GRAPH_FILE.exists() else []),
        "lossless_archive": str(LEGACY_ARCHIVE_FILE.relative_to(ROOT)).replace("\\", "/"),
        "output": str(CANONICAL_OUTPUT_FILE.relative_to(ROOT)).replace("\\", "/"),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CANONICAL_OUTPUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    LEGACY_ARCHIVE_FILE.write_text(json.dumps(legacy_archive, indent=2), encoding="utf-8")
    MIGRATION_REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _empty_canonical_mission(mission_id: str, title: str) -> dict[str, Any]:
    return {
        "id": mission_id,
        "title": title,
        "objective": "",
        "objectives": [],
        "strategic_alignment": {
            "themes": ["platform_stability", "interoperability"],
            "target_platforms": ["IS_BACKOFFICE", "ING_DIGHUB"],
            "rationale": "Canonical mission alignment migration",
        },
        "value": {"business_value": 0.0, "engineering_value": 0.0, "knowledge_value": 0.0},
        "hypothesis_portfolio_ids": [],
        "scoring_matrix": {
            "architecture": 0.0,
            "maintainability": 0.0,
            "scalability": 0.0,
            "performance": 0.0,
            "interoperability": 0.0,
            "governance": 0.0,
        },
        "work_packages": [],
        "dependencies": [],
        "capabilities": [],
        "evidence_ids": [],
        "deliverables": [],
        "risks": [],
        "kpis": [],
        "milestones": [],
        "lessons_learned": [],
        "mission_state": "planned",
        "mission_history": [],
        "mission_evolution": [],
        "mission_score": 0.0,
        "mission_roi": 0.0,
        "mission_confidence": 0.0,
        "mission_traceability": {
            "source_documents": [],
            "evidence_ids": [],
            "dependency_links": [],
        },
        "mission_knowledge_assets": [],
        "status": "planned",
        "tags": ["migrated"],
        "created_at": "2026-07-24T00:00:00Z",
        "updated_at": "2026-07-24T00:00:00Z",
    }


if __name__ == "__main__":
    print(json.dumps(migrate(), indent=2))
