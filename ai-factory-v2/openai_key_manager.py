"""Central OpenAI API key loader for AI Factory v2."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional


_PLACEHOLDER_KEY = "paste-your-openai-api-key-here"


class OpenAIMasterKeyManager:
    """Read the OpenAI key from the shared master JSON file."""

    _instance: Optional["OpenAIMasterKeyManager"] = None

    def __new__(cls) -> "OpenAIMasterKeyManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
            cls._instance._master_file_path = None
            cls._instance._api_key = None
            cls._instance._org_id = None
            cls._instance._project_id = None
        return cls._instance

    def __init__(self) -> None:
        if not self._loaded:
            self.refresh()

    def _candidate_paths(self) -> list[Path]:
        repo_root = Path(__file__).resolve().parent.parent
        candidates = [repo_root / ".openai-master-key.json"]

        override_path = os.environ.get("AI_FACTORY_OPENAI_MASTER_KEY", "").strip()
        if override_path:
            candidates.insert(0, Path(override_path))

        ai_factory_path = os.environ.get("AI_FACTORY_PATH", "").strip()
        if ai_factory_path:
            candidates.append(Path(ai_factory_path) / ".openai-master-key.json")

        cwd_candidate = Path.cwd() / ".openai-master-key.json"
        if cwd_candidate not in candidates:
            candidates.append(cwd_candidate)

        return candidates

    def _locate_master_file(self) -> Optional[Path]:
        for path in self._candidate_paths():
            if path.exists():
                return path
        return None

    def _load_data(self) -> dict[str, Any]:
        path = self._locate_master_file()
        self._master_file_path = path
        if path is None:
            return {}

        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _clean_value(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return None
        cleaned = value.strip()
        if not cleaned or cleaned == _PLACEHOLDER_KEY:
            return None
        return cleaned

    def refresh(self) -> None:
        data = self._load_data()
        openai_config = data.get("openai", {}) if isinstance(data, dict) else {}
        self._api_key = self._clean_value(openai_config.get("api_key"))
        self._org_id = self._clean_value(openai_config.get("organization_id"))
        self._project_id = self._clean_value(openai_config.get("project_id"))
        self._loaded = True

    def get_api_key(self) -> Optional[str]:
        env_key = self._clean_value(os.environ.get("OPENAI_API_KEY"))
        return self._api_key or env_key

    def get_organization_id(self) -> Optional[str]:
        return self._org_id

    def get_project_id(self) -> Optional[str]:
        return self._project_id

    def get_master_file_path(self) -> Optional[Path]:
        return self._master_file_path

    def set_environment_variable(self) -> bool:
        api_key = self.get_api_key()
        if not api_key:
            return False
        os.environ["OPENAI_API_KEY"] = api_key
        if self._org_id:
            os.environ["OPENAI_ORG_ID"] = self._org_id
        if self._project_id:
            os.environ["OPENAI_PROJECT_ID"] = self._project_id
        return True


_manager: Optional[OpenAIMasterKeyManager] = None


def get_openai_manager() -> OpenAIMasterKeyManager:
    global _manager
    if _manager is None:
        _manager = OpenAIMasterKeyManager()
    return _manager


def get_openai_api_key() -> Optional[str]:
    return get_openai_manager().get_api_key()


def setup_openai_env() -> bool:
    return get_openai_manager().set_environment_variable()


if __name__ == "__main__":
    manager = get_openai_manager()
    key = manager.get_api_key()
    if not key:
        print("No OpenAI API key configured.")
    else:
        masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
        print(f"Master file: {manager.get_master_file_path()}")
        print(f"OpenAI API key loaded: {masked}")