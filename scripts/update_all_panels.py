"""Update all dashboard panel data files from synced/cascade outputs."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(r"C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2")
DATA_DIR = ROOT / "data"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def to_float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def update_action_dashboard(cascade: Dict[str, Any]) -> Dict[str, Any]:
    dashboard = cascade.get("actions_generated", {}).get("dashboard", {})
    write_json(DATA_DIR / "action_dashboard.json", dashboard)
    return {"total_actions": dashboard.get("statistics", {}).get("total_actions", 0)}


def update_offers_panel(offers: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = {
        "total_offers": len(offers),
        "by_status": {},
        "by_kam": {},
        "total_value": 0.0,
        "expected_revenue": 0.0,
        "last_updated": datetime.now(UTC).isoformat(),
    }
    for offer in offers:
        status = str(offer.get("status") or "unknown")
        summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

        kam = str(offer.get("kam_name") or "unassigned")
        summary["by_kam"][kam] = summary["by_kam"].get(kam, 0) + 1

        amount = to_float(offer.get("total_amount") or offer.get("total_value") or offer.get("estimated_value"))
        summary["total_value"] += amount
        summary["expected_revenue"] += amount * (to_float(offer.get("expected_success_rate"),) / 100.0 if offer.get("expected_success_rate") is not None else 0.5)

    summary["total_value"] = round(summary["total_value"], 2)
    summary["expected_revenue"] = round(summary["expected_revenue"], 2)
    write_json(DATA_DIR / "offers_panel.json", summary)
    return summary


def update_kam_dashboard(offers: List[Dict[str, Any]]) -> Dict[str, Any]:
    kams: Dict[str, Dict[str, Any]] = {}
    for offer in offers:
        kam = str(offer.get("kam_name") or "unassigned")
        item = kams.setdefault(
            kam,
            {
                "total_offers": 0,
                "total_value": 0.0,
                "expected_revenue": 0.0,
            },
        )
        item["total_offers"] += 1
        value = to_float(offer.get("total_amount") or offer.get("total_value") or 0)
        item["total_value"] += value
        success = to_float(offer.get("expected_success_rate"), 50.0) / 100.0
        item["expected_revenue"] += value * success

    for item in kams.values():
        item["total_value"] = round(item["total_value"], 2)
        item["expected_revenue"] = round(item["expected_revenue"], 2)

    write_json(DATA_DIR / "kam_dashboard.json", kams)
    return kams


def update_action_pool_panel(cascade: Dict[str, Any]) -> Dict[str, Any]:
    dashboard = cascade.get("actions_generated", {}).get("dashboard", {})
    role_view: Dict[str, Any] = {}
    for role, data in dashboard.items():
        if role == "statistics":
            continue
        if int(data.get("total_pending", 0)) <= 0:
            continue
        role_view[role] = {
            "pending": data.get("total_pending", 0),
            "critical": data.get("critical", 0),
            "high": data.get("high", 0),
            "top_actions": data.get("actions", [])[:5],
        }

    payload = {
        "by_role": role_view,
        "statistics": dashboard.get("statistics", {}),
        "last_updated": datetime.now(UTC).isoformat(),
    }
    write_json(DATA_DIR / "action_pool_panel.json", payload)
    return payload


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    offers = read_json(DATA_DIR / "synced_offers.json", [])
    cascade = read_json(DATA_DIR / "cascade_results.json", {})

    a = update_action_dashboard(cascade)
    o = update_offers_panel(offers)
    k = update_kam_dashboard(offers)
    p = update_action_pool_panel(cascade)

    print("=" * 70)
    print("PANELS UPDATED")
    print("=" * 70)
    print(f"action_dashboard.total_actions: {a.get('total_actions', 0)}")
    print(f"offers_panel.total_offers: {o.get('total_offers', 0)}")
    print(f"kam_dashboard.kams: {len(k)}")
    print(f"action_pool_panel.roles: {len(p.get('by_role', {}))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
