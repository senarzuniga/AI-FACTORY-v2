"""Verify completeness of forced update outputs."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict

ROOT = Path(r"C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2")
DATA_DIR = ROOT / "data"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> int:
    required = [
        "synced_offers.json",
        "synced_customers.json",
        "synced_requests.json",
        "cascade_results.json",
        "action_dashboard.json",
        "offers_panel.json",
        "kam_dashboard.json",
        "action_pool_panel.json",
    ]

    result: Dict[str, Any] = {
        "status": "OK",
        "timestamp": datetime.now(UTC).isoformat(),
        "components": {},
        "errors": [],
    }

    for file_name in required:
        fp = DATA_DIR / file_name
        if fp.exists():
            result["components"][file_name] = {
                "status": "OK",
                "size": fp.stat().st_size,
            }
        else:
            result["components"][file_name] = {"status": "MISSING", "size": 0}
            result["errors"].append(f"Missing file: {file_name}")

    offers = read_json(DATA_DIR / "synced_offers.json", [])
    action_pool = read_json(DATA_DIR / "action_pool_panel.json", {})
    stats = action_pool.get("statistics", {}) if isinstance(action_pool, dict) else {}

    result["metrics"] = {
        "offers_count": len(offers) if isinstance(offers, list) else 0,
        "actions_total": stats.get("total_actions", 0),
        "actions_pending": stats.get("pending", 0),
        "actions_completed": stats.get("completed", 0),
    }

    if result["errors"]:
        result["status"] = "INCOMPLETE"

    (DATA_DIR / "verification_report.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print(f"status: {result['status']}")
    print(f"offers_count: {result['metrics']['offers_count']}")
    print(f"actions_total: {result['metrics']['actions_total']}")
    print(f"errors: {len(result['errors'])}")
    if result["errors"]:
        for err in result["errors"]:
            print(f" - {err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
