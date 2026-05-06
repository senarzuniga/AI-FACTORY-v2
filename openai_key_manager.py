"""Workspace-level wrapper for the AI Factory v2 OpenAI key manager."""

from __future__ import annotations

import importlib.util
from pathlib import Path


_IMPL_PATH = Path(__file__).resolve().parent / "ai-factory-v2" / "openai_key_manager.py"
_SPEC = importlib.util.spec_from_file_location("_ai_factory_openai_key_manager", _IMPL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Cannot load OpenAI key manager from {_IMPL_PATH}")

_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

OpenAIMasterKeyManager = _MODULE.OpenAIMasterKeyManager
get_openai_manager = _MODULE.get_openai_manager
get_openai_api_key = _MODULE.get_openai_api_key
setup_openai_env = _MODULE.setup_openai_env

__all__ = [
    "OpenAIMasterKeyManager",
    "get_openai_manager",
    "get_openai_api_key",
    "setup_openai_env",
]