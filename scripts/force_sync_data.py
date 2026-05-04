"""Forced sync of sales data into AI-FACTORY local data folder."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

AI_FACTORY = Path(r"C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2")
SALES_ENGINE = Path(r"C:\Users\Inaki Senar\Documents\GitHub\adaptive-sales-engine")
DATA_DIR = AI_FACTORY / "data"


def parse_env(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def fetch_table(base_url: str, api_key: str, table: str, limit: int = 5000) -> Tuple[List[Dict[str, Any]], str]:
    endpoint = f"{base_url.rstrip('/')}/rest/v1/{table}?select=*&limit={limit}"
    req = Request(
        endpoint,
        headers={
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            if isinstance(payload, list):
                return payload, "ok"
            return [], "non_list_payload"
    except HTTPError as exc:
        return [], f"http_{exc.code}"
    except URLError as exc:
        return [], f"url_error:{exc.reason}"
    except Exception as exc:  # pragma: no cover
        return [], f"error:{exc}"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    print("=" * 70)
    print("FORCED DATA SYNC")
    print("=" * 70)

    env = parse_env(SALES_ENGINE / ".env")
    supabase_url = env.get("SUPABASE_URL") or env.get("VITE_SUPABASE_URL") or env.get("NEXT_PUBLIC_SUPABASE_URL")
    service_key = env.get("SUPABASE_SERVICE_ROLE_KEY") or env.get("SUPABASE_SECRET_KEY")

    summary: Dict[str, Any] = {
        "sync_status": "started",
        "source": str(SALES_ENGINE),
        "supabase_url_detected": bool(supabase_url),
        "service_key_detected": bool(service_key),
        "tables": {},
    }

    offers: List[Dict[str, Any]] = []
    customers: List[Dict[str, Any]] = []
    requests_data: List[Dict[str, Any]] = []

    if supabase_url and service_key:
        offers, offers_state = fetch_table(supabase_url, service_key, "offers")
        companies, companies_state = fetch_table(supabase_url, service_key, "companies")
        contradictions, contradictions_state = fetch_table(supabase_url, service_key, "ingestion_contradictions")

        customers = companies
        requests_data = [c for c in contradictions if str(c.get("status", "")).lower() == "pending"]

        # If there are no pending contradictions, synthesize lightweight requests from companies
        # so downstream agent cascades still produce actionable tasks.
        if not requests_data and customers:
            requests_data = [
                {
                    "entity_name": c.get("company_name") or c.get("name") or "unknown",
                    "field_name": "company_profile_refresh",
                    "notes": f"Revisar y activar acciones para {c.get('company_name') or c.get('name') or 'cliente'}",
                    "status": "pending",
                }
                for c in customers[:10]
            ]

        summary["tables"]["offers"] = {"state": offers_state, "count": len(offers)}
        summary["tables"]["companies"] = {"state": companies_state, "count": len(customers)}
        summary["tables"]["ingestion_contradictions"] = {"state": contradictions_state, "count": len(contradictions)}
    else:
        summary["tables"]["offers"] = {"state": "missing_supabase_credentials", "count": 0}
        summary["tables"]["companies"] = {"state": "missing_supabase_credentials", "count": 0}
        summary["tables"]["ingestion_contradictions"] = {"state": "missing_supabase_credentials", "count": 0}

    # Fallbacks so downstream panels always update deterministically.
    fallback_offers = DATA_DIR / "synced_offers.json"
    if not offers and fallback_offers.exists():
        try:
            offers = json.loads(fallback_offers.read_text(encoding="utf-8"))
            summary["tables"]["offers"]["state"] = "fallback_existing_file"
            summary["tables"]["offers"]["count"] = len(offers)
        except Exception:
            pass

    write_json(DATA_DIR / "synced_offers.json", offers)
    write_json(DATA_DIR / "synced_customers.json", customers)
    write_json(DATA_DIR / "synced_requests.json", requests_data)

    summary["sync_status"] = "completed"
    write_json(DATA_DIR / "sync_summary.json", summary)

    print(f"Offers synced: {len(offers)}")
    print(f"Customers synced: {len(customers)}")
    print(f"Pending requests synced: {len(requests_data)}")
    print(f"Data folder: {DATA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
