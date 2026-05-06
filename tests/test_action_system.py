"""Smoke test for Action Engine + Request Management integration."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


async def main() -> None:
    from agents.action_engine import ActionGenerator, ActionOrchestrator, ActionPool
    from agents.request_management.request_management_agent import RequestManagementAgent

    pool = ActionPool()
    orchestrator = ActionOrchestrator(pool, ActionGenerator(pool))

    actions = await orchestrator.process_and_generate_actions(
        "new_request",
        {
            "request": {
                "company_name": "PlasticTech Solutions",
                "requirements": ["Integracion con ERP", "Formacion"],
            },
            "company_info": {"name": "PlasticTech Solutions"},
        },
    )
    print(f"ActionEngine generated: {len(actions)}")
    assert len(actions) >= 2

    agent = RequestManagementAgent("url", "key", "http://localhost:5173")
    await agent.initialize()
    req = await agent.process_request(
        "Empresa: MetalWorks SA. Solicitamos oferta para linea automatizada. Contacto: compras@metalworks.com"
    )
    print(f"Request processed: {req.id}")
    print(f"Request actions generated: {len(req.generated_actions)}")
    assert req.status.value == "completed"
    assert len(req.generated_actions) >= 1
    await agent.close()

    stats = pool.get_statistics()
    print(f"Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
