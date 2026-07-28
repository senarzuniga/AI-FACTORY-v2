from __future__ import annotations

import asyncio
import os
from unittest.mock import patch

from context.context_layer import UserRole
from orchestrator.hybrid_orchestrator import HybridOrchestrator


def _run(orchestrator: HybridOrchestrator):
    return asyncio.run(
        orchestrator.run(
            prompt="Genera una propuesta comercial con prioridad alta",
            user_id="qa.user@example.com",
            client="Ingercart",
            role=UserRole.ADMIN,
        )
    )


def test_production_requires_human_approval_by_default():
    with patch.dict(os.environ, {"AI_FACTORY_ENV": "production"}, clear=False):
        orch = HybridOrchestrator()
        result = _run(orch)

    assert result["status"] == "pending_human_review"
    assert result["message"] == "En espera de aprobacion humana."


def test_non_production_allows_auto_approval():
    with patch.dict(os.environ, {"AI_FACTORY_ENV": "development"}, clear=False):
        orch = HybridOrchestrator()
        result = _run(orch)

    assert result["status"] == "completed"
    assert result["quality"]["passed"] in {True, False}
