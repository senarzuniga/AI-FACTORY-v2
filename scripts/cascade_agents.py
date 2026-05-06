"""Cascade execution across available agents with robust fallbacks."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(r"C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2")
DATA_DIR = ROOT / "data"
sys.path.insert(0, str(ROOT))


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


class CascadeExecutor:
    def __init__(self) -> None:
        self.results: Dict[str, Any] = {
            "dynamic_pricing": [],
            "cross_selling": [],
            "request_management": [],
            "actions_generated": {"actions": [], "dashboard": {}},
            "errors": [],
            "started_at": datetime.now(UTC).isoformat(),
        }

    async def run(self) -> Dict[str, Any]:
        offers = read_json(DATA_DIR / "synced_offers.json", [])
        customers = read_json(DATA_DIR / "synced_customers.json", [])
        requests_data = read_json(DATA_DIR / "synced_requests.json", [])

        self.results["dynamic_pricing"] = await self._dynamic_pricing(offers)
        self.results["cross_selling"] = await self._cross_selling(offers, customers)
        self.results["request_management"] = await self._request_management(requests_data)
        self.results["actions_generated"] = await self._action_engine(offers, customers, requests_data)

        self.results["completed_at"] = datetime.now(UTC).isoformat()
        return self.results

    async def _dynamic_pricing(self, offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Fallback heuristic pricing based on expected success and amount.
        out: List[Dict[str, Any]] = []
        for offer in offers[:50]:
            base = to_float(offer.get("total_amount") or offer.get("total_value") or offer.get("estimated_value"), 0.0)
            success = to_float(offer.get("expected_success_rate"), 50.0)
            factor = 0.97 if success >= 80 else (1.00 if success >= 60 else 1.03)
            optimal = round(base * factor, 2)
            out.append(
                {
                    "offer_id": offer.get("id"),
                    "offer_number": offer.get("offer_number"),
                    "optimal_price": optimal,
                    "strategy": "retain_margin" if factor >= 1 else "increase_win_rate",
                    "confidence": round(min(max(success / 100.0, 0.2), 0.95), 2),
                }
            )
        return out

    async def _cross_selling(self, offers: List[Dict[str, Any]], customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_customer: Dict[str, List[Dict[str, Any]]] = {}
        for offer in offers:
            cid = str(offer.get("company_id") or offer.get("customer_id") or "")
            if not cid:
                continue
            by_customer.setdefault(cid, []).append(offer)

        out: List[Dict[str, Any]] = []
        for customer in customers[:200]:
            cid = str(customer.get("id") or "")
            if not cid:
                continue
            c_offers = by_customer.get(cid, [])
            if len(c_offers) < 2:
                continue
            potential = round(sum(to_float(o.get("total_amount") or o.get("total_value"), 0.0) for o in c_offers) * 0.12, 2)
            out.append(
                {
                    "customer_id": cid,
                    "customer_name": customer.get("company_name") or customer.get("name"),
                    "opportunities": max(1, len(c_offers) // 2),
                    "potential_value": potential,
                }
            )
        return out

    async def _request_management(self, requests_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        try:
            from agents.request_management.request_management_agent import RequestManagementAgent

            agent = RequestManagementAgent("", "", "http://localhost:5173")
            await agent.initialize()
            for req in requests_data[:50]:
                text = req.get("notes") or req.get("description") or req.get("field_name") or "Pending contradiction request"
                processed = await agent.process_request(str(text))
                out.append(
                    {
                        "request_id": processed.id,
                        "type": processed.type.value,
                        "actions_generated": len(processed.generated_actions),
                    }
                )
            await agent.close()
        except Exception as exc:
            self.results["errors"].append(f"request_management:{exc}")
        return out

    async def _action_engine(
        self,
        offers: List[Dict[str, Any]],
        customers: List[Dict[str, Any]],
        requests_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            from agents.action_engine import ActionGenerator, ActionOrchestrator, ActionPool

            pool = ActionPool()
            generator = ActionGenerator(pool)
            orchestrator = ActionOrchestrator(pool, generator)

            actions = []
            for req in requests_data[:20]:
                payload = {
                    "request": {
                        "company_name": req.get("entity_name") or req.get("company_name") or "unknown",
                        "requirements": [req.get("field_name")] if req.get("field_name") else [],
                    },
                    "company_info": {},
                }
                actions.extend(await orchestrator.process_and_generate_actions("new_request", payload))

            # Fallback: if no requests arrived, generate minimal request actions from customers.
            if not actions and customers:
                for customer in customers[:10]:
                    payload = {
                        "request": {
                            "company_name": customer.get("company_name") or customer.get("name") or "unknown",
                            "requirements": ["account_review"],
                        },
                        "company_info": {"name": customer.get("company_name") or customer.get("name")},
                    }
                    actions.extend(await orchestrator.process_and_generate_actions("new_request", payload))

            # Inject opportunity actions from cross-selling output.
            cross_items = await self._cross_selling(offers, customers)
            for item in cross_items[:20]:
                payload = {
                    "opportunity": {
                        "product": "cross_selling_bundle",
                        "potential_value": item.get("potential_value", 0),
                    },
                    "customer": {"name": item.get("customer_name"), "lifetime_value": 0.6},
                }
                actions.extend(await orchestrator.process_and_generate_actions("opportunity_detected", payload))

            return {
                "actions": [
                    {
                        "id": a.id,
                        "title": a.title,
                        "priority": a.priority.name,
                        "role": a.role.value,
                        "score": a.score,
                    }
                    for a in actions
                ],
                "dashboard": orchestrator.get_actions_dashboard(),
            }
        except Exception as exc:
            self.results["errors"].append(f"action_engine:{exc}")
            return {"actions": [], "dashboard": {}}


async def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    executor = CascadeExecutor()
    results = await executor.run()
    (DATA_DIR / "cascade_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=" * 70)
    print("CASCADE EXECUTION COMPLETE")
    print("=" * 70)
    print(f"Dynamic pricing items: {len(results['dynamic_pricing'])}")
    print(f"Cross-selling items: {len(results['cross_selling'])}")
    print(f"Request management items: {len(results['request_management'])}")
    print(f"Actions generated: {len(results['actions_generated'].get('actions', []))}")
    print(f"Errors: {len(results['errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
