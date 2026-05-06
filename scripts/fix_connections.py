"""Validate and repair local connections between AI-FACTORY and adaptive-sales-engine."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(r"C:\Users\Inaki Senar\Documents\GitHub\AI-FACTORY-v2")
APP = Path(r"C:\Users\Inaki Senar\Documents\GitHub\adaptive-sales-engine")
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def probe(url: str, timeout: int = 3) -> tuple[bool, int | None]:
    req = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as response:
            return 200 <= response.status < 400, response.status
    except HTTPError as exc:
        return False, exc.code
    except URLError:
        return False, None
    except Exception:
        return False, None


def check_sales_engine() -> dict[str, Any]:
    candidate_ports = [5173, 3000, 8081, 8082, 5000]
    for port in candidate_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.7)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return {
                    "status": "connected",
                    "url": f"http://localhost:{port}",
                    "port": port,
                    "http_code": None,
                    "last_check": utc_now(),
                    "detection": "tcp_port_open",
                }

    candidates: list[tuple[int, str]] = [
        (5173, "/api/health"),
        (3000, "/api/health"),
        (8081, "/api/health"),
        (8082, "/api/health"),
        (5173, "/health"),
        (3000, "/health"),
        (8081, "/health"),
        (8082, "/health"),
        (5173, "/"),
        (3000, "/"),
        (8081, "/"),
        (8082, "/"),
        (5000, "/"),
    ]

    for port, route in candidates:
        url = f"http://localhost:{port}{route}"
        ok, code = probe(url)
        if ok:
            return {
                "status": "connected",
                "url": url,
                "port": port,
                "http_code": code,
                "last_check": utc_now(),
                "detection": "http_probe",
            }

    return {
        "status": "disconnected",
        "url": None,
        "port": None,
        "http_code": None,
        "last_check": utc_now(),
    }


def check_hub_api() -> dict[str, Any]:
    url = "http://localhost:8000/hub/status"
    ok, code = probe(url)
    return {
        "status": "connected" if ok else "disconnected",
        "url": url,
        "http_code": code,
        "last_check": utc_now(),
    }


def check_teams() -> dict[str, Any]:
    # External network might be blocked; we keep integration as configured URL.
    return {
        "status": "configured",
        "url": "https://teams.live.com/l/community/FEA5JSTpd_3FAKh9gI",
        "last_check": utc_now(),
    }


def ensure_data_files() -> dict[str, Any]:
    required = [
        "synced_offers.json",
        "synced_customers.json",
        "synced_requests.json",
        "action_dashboard.json",
        "offers_panel.json",
        "kam_dashboard.json",
        "action_pool_panel.json",
    ]

    missing: list[str] = []
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name in required:
        fp = DATA_DIR / name
        if fp.exists():
            continue
        missing.append(name)
        default_payload: Any = [] if name.startswith("synced_") else {}
        write_json(fp, default_payload)

    return {
        "required": required,
        "missing_before_fix": missing,
        "status": "ready",
        "last_check": utc_now(),
    }


def discover_agents() -> dict[str, Any]:
    agents: list[str] = []
    for pattern in ("agents/*_agent.py", "agents/request_management/*_agent.py"):
        for fp in ROOT.glob(pattern):
            agents.append(fp.name)
    agents = sorted(set(agents))
    return {
        "status": "detected" if agents else "none",
        "count": len(agents),
        "agents": agents,
        "last_check": utc_now(),
    }


def write_api_routes() -> Path:
    routes = {
        "sales_engine": {
            "health_candidates": [
                "http://localhost:5173/api/health",
                "http://localhost:3000/api/health",
                "http://localhost:8081/api/health",
                "http://localhost:8082/api/health",
                "http://localhost:5173/health",
                "http://localhost:3000/health",
                "http://localhost:8081/health",
                "http://localhost:8082/health",
                "http://localhost:5173/",
                "http://localhost:8082/",
            ]
        },
        "orchestrator": {
            "panel": "http://localhost:8080/dashboard/orchestrator_panel.html",
            "hub_api": "http://localhost:8000/hub/status",
            "technical_dashboard": "http://localhost:8501",
            "human_portal": "http://localhost:8502",
        },
        "teams": {
            "channel": "https://teams.live.com/l/community/FEA5JSTpd_3FAKh9gI"
        },
    }
    target = CONFIG_DIR / "api_routes.json"
    write_json(target, routes)
    return target


def write_start_all() -> Path:
    content = f"""# Unified quick start helper generated by scripts/fix_connections.py
param(
    [string]$OrchestratorPath = \"{ROOT}\",
    [string]$AppPath = \"{APP}\"
)

$ErrorActionPreference = \"Stop\"
Set-Location $OrchestratorPath
Write-Host \"Starting ecosystem from $OrchestratorPath\" -ForegroundColor Cyan

if (Test-Path \"$OrchestratorPath\\start_ecosystem.ps1\") {{
    & \"$OrchestratorPath\\start_ecosystem.ps1\" -OrchestratorPath $OrchestratorPath -AppPath $AppPath
}} else {{
    Write-Host \"start_ecosystem.ps1 was not found.\" -ForegroundColor Red
    exit 1
}}
"""
    target = ROOT / "start_all.ps1"
    target.write_text(content, encoding="utf-8")
    return target


def try_start_sales_engine() -> dict[str, Any]:
    if not APP.exists():
        return {"attempted": False, "reason": "app_path_missing"}

    package_json = APP / "package.json"
    if not package_json.exists():
        return {"attempted": False, "reason": "package_json_missing"}

    try:
        subprocess.Popen(
            [
                "powershell",
                "-NoExit",
                "-Command",
                f"cd '{APP}' ; npm run dev",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {"attempted": True, "reason": "npm_run_dev_started"}
    except Exception as exc:
        return {"attempted": True, "reason": f"start_failed:{exc}"}


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    start_missing = "--start-missing" in argv

    report: dict[str, Any] = {
        "timestamp": utc_now(),
        "paths": {
            "orchestrator": str(ROOT),
            "app": str(APP),
        },
    }

    report["sales_engine"] = check_sales_engine()
    if start_missing and report["sales_engine"]["status"] != "connected":
        report["sales_engine_start_attempt"] = try_start_sales_engine()

    report["hub_api"] = check_hub_api()
    report["teams"] = check_teams()
    report["data_files"] = ensure_data_files()
    report["agents"] = discover_agents()

    routes_path = write_api_routes()
    start_all_path = write_start_all()

    report["artifacts"] = {
        "api_routes": str(routes_path),
        "start_all": str(start_all_path),
    }

    status = "ok"
    if report["sales_engine"]["status"] != "connected":
        status = "warning"
    if report["agents"]["count"] == 0:
        status = "warning"

    report["status"] = status
    output_path = DATA_DIR / "connection_status.json"
    write_json(output_path, report)

    print("=" * 70)
    print("CONNECTION CHECK")
    print("=" * 70)
    print(f"sales_engine: {report['sales_engine']['status']}")
    print(f"hub_api: {report['hub_api']['status']}")
    print(f"agents_detected: {report['agents']['count']}")
    print(f"data_files_status: {report['data_files']['status']}")
    print(f"report: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
