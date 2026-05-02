"""Top-level entrypoint for AI-FACTORY-v2 advanced protocol orchestrator."""

from __future__ import annotations

import asyncio
from pathlib import Path

from orchestrator.main import run_from_config
from orchestrator.utils.config import load_config
from orchestrator.utils.logger import configure_logger, get_logger


async def _main() -> int:
    config_path = Path("config.yaml")
    config = load_config(config_path)

    configure_logger(config.get("monitoring", {}).get("log_level", "INFO"))
    logger = get_logger("main")

    logger.info("Starting AI-FACTORY-v2 advanced orchestrator")
    result = await run_from_config(config)
    logger.info("Orchestration finished with status: %s", result.get("status", "unknown"))
    logger.info("Applied changes: %d | Failed changes: %d", len(result.get("applied", [])), len(result.get("failed", [])))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
