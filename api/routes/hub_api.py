"""FastAPI routes for the collaborative hub."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from agents.action_engine import ActionPool
from api.action_dashboard import create_action_router

APP_STARTED_AT = datetime.now(timezone.utc)
REPO_ROOT = Path(__file__).resolve().parents[2]

app = FastAPI(title="Ingercart Collaborative Hub API", version="1.0.0")

# Optional enhancement: shared in-memory action pool for dashboard endpoints.
_action_pool = ActionPool()
app.include_router(create_action_router(_action_pool))


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "collaborative-hub-api",
        "status": "ok",
        "message": "Ingercart collaborative hub API is running",
    }


@app.get("/hub/status")
def hub_status() -> dict[str, Any]:
    uptime_seconds = int((datetime.now(timezone.utc) - APP_STARTED_AT).total_seconds())
    return {
        "status": "online",
        "client": "Ingercart",
        "uptime_seconds": uptime_seconds,
        "started_at": APP_STARTED_AT.isoformat(),
    }


@app.get("/hub/config")
def hub_config() -> dict[str, Any]:
    config_file = REPO_ROOT / "config" / "collaborative_hub.json"
    if not config_file.exists():
        return {"status": "missing", "config_path": str(config_file)}

    import json

    return {
        "status": "loaded",
        "config_path": str(config_file),
        "config": json.loads(config_file.read_text(encoding="utf-8")),
    }
