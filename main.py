"""
Top-level entrypoint for AI-FACTORY-v2.

Modes
-----
- default        : advanced protocol orchestrator (EPOCH / I-MCTS / GNAP / Co-EPG)
- --agentic      : complete agentic system for Ingercart
                   (Context Layer + Supervisor + Dual Generation + Judge + Human-in-the-loop)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path


# ──────────────────────────────────────────────────────────
# ADVANCED PROTOCOL ORCHESTRATOR (default)
# ──────────────────────────────────────────────────────────

async def _run_protocol_orchestrator() -> int:
    from orchestrator.main import run_from_config
    from orchestrator.utils.config import load_config
    from orchestrator.utils.logger import configure_logger, get_logger

    config_path = Path("config.yaml")
    config = load_config(config_path)

    configure_logger(config.get("monitoring", {}).get("log_level", "INFO"))
    logger = get_logger("main")

    logger.info("Starting AI-FACTORY-v2 advanced orchestrator")
    result = await run_from_config(config)
    logger.info(
        "Orchestration finished with status: %s", result.get("status", "unknown")
    )
    logger.info(
        "Applied changes: %d | Failed changes: %d",
        len(result.get("applied", [])),
        len(result.get("failed", [])),
    )
    return 0


# ──────────────────────────────────────────────────────────
# AGENTIC SYSTEM - INGERCART (--agentic flag)
# ──────────────────────────────────────────────────────────

async def _run_agentic_system() -> int:
    from orchestrator.hybrid_orchestrator import HybridOrchestrator
    from context.context_layer import UserRole

    print("SISTEMA MULTI-AGENTE - AI-FACTORY-v2 / INGERCART")
    print("Capacidades:")
    print("  - Context Layer (control de datos por cliente)")
    print("  - Supervisor Agent (intencion y workflow)")
    print("  - Dual Generation + Judge (calidad superior)")
    print("  - Human-in-the-loop (decisiones criticas)")
    print("  - Memory per client (aprendizaje continuo)")
    print()

    orchestrator = HybridOrchestrator()

    result = await orchestrator.run(
        prompt=(
            "Analiza las ventas del ultimo trimestre y genera "
            "una propuesta de mejora para Ingercart"
        ),
        user_id="isenar.cta@gmail.com",
        client="Ingercart",
        role=UserRole.ADMIN,
    )

    print()
    print("RESULTADO:")
    print(f"  Status       : {result['status']}")
    print(f"  Intent       : {result['intent']}")
    print(f"  Agents used  : {result['workflow']['agents_used']}")
    print(f"  Quality OK   : {result.get('quality', {}).get('passed', 'n/a')}")
    return 0


# ──────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--cascade" in sys.argv:
        from cascade_orchestrator import run_cli_async

        cascade_args = [a for a in sys.argv[1:] if a != "--cascade"]
        raise SystemExit(asyncio.run(run_cli_async(cascade_args)))
    if "--agentic" in sys.argv:
        raise SystemExit(asyncio.run(_run_agentic_system()))
    raise SystemExit(asyncio.run(_run_protocol_orchestrator()))
