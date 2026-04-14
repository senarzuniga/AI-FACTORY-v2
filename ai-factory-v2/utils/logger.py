"""
AI Factory v2 — Structured logger
"""
from __future__ import annotations

import logging
import sys
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with consistent formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_section(logger: logging.Logger, title: str) -> None:
    """Print a visible section separator in the logs."""
    separator = "─" * 60
    logger.info(separator)
    logger.info("  %s", title)
    logger.info(separator)


def log_dict(logger: logging.Logger, label: str, data: dict[str, Any]) -> None:
    """Pretty-print a dictionary to the log."""
    logger.info("%s:", label)
    for key, value in data.items():
        logger.info("    %-30s %s", f"{key}:", value)
