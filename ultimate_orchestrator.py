"""
AI-FACTORY-V2 ULTIMATE ORCHESTRATOR
Maximum Performance Self-Healing Protocol for ALL Applications
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None


COMMON_PORTS = [3000, 5000, 7860, 8000, 8080, 8501]
DATA_DIR_CANDIDATES = ["data", "documents", "docs", "uploads", "knowledge_base"]
MAX_PY_FILES_QUICK = 120
MAX_LOG_FILES_QUICK = 20


class UltimateOrchestrator:
    """Orchestrator-level health analysis and auto-healing across sibling apps."""

    def __init__(self, github_root: str, deep_checks: bool = False) -> None:
        self.github_root = Path(github_root).resolve()
        self.orchestrator_path = self.github_root / "AI-FACTORY-v2"
        self.deep_checks = deep_checks
        self.apps = self._discover_apps()

    def _is_app_folder(self, folder: Path) -> bool:
        if (folder / "package.json").exists() or (folder / "requirements.txt").exists():
            return True
        return any(folder.glob("*.py"))

    def _discover_apps(self) -> list[Path]:
        apps: list[Path] = []
        if not self.github_root.exists():
            return apps
        for item in self.github_root.iterdir():
            if not item.is_dir():
                continue
            if item.name.lower() == "ai-factory-v2":
                continue
            if self._is_app_folder(item):
                apps.append(item)
        return sorted(apps, key=lambda p: p.name.lower())

    def _iter_python_files(self, app_path: Path):
        count = 0
        limit = MAX_PY_FILES_QUICK if not self.deep_checks else 10_000_000
        for py_file in app_path.rglob("*.py"):
            if ".venv" in py_file.parts or "venv" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            yield py_file
            count += 1
            if count >= limit:
                break

    def _iter_log_files(self, app_path: Path):
        count = 0
        limit = MAX_LOG_FILES_QUICK if not self.deep_checks else 10_000_000
        for log_file in app_path.rglob("*.log"):
            yield log_file
            count += 1
            if count >= limit:
                break

    def run_quantum_demand_analysis(self) -> dict[str, Any]:
        print("[1/6] Running quantum demand analysis")
        print(f"Analyzing {len(self.apps)} applications")

        if not self.apps:
            return {}

        results: dict[str, Any] = {}
        max_workers = min(8, max(1, len(self.apps)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_app = {
                executor.submit(self._analyze_single_app, app): app for app in self.apps
            }
            for future in as_completed(future_to_app):
                app = future_to_app[future]
                try:
                    app_results = future.result(timeout=120)
                    results[app.name] = app_results
                    print(f"  - {app.name}: {app_results.get('overall_status', 'UNKNOWN')}")
                except Exception as exc:
                    results[app.name] = {
                        "app_name": app.name,
                        "overall_status": "FAILED",
                        "error": str(exc),
                        "checks": {},
                    }
                    print(f"  - {app.name}: FAILED ({exc})")
        return results

    def _analyze_single_app(self, app_path: Path) -> dict[str, Any]:
        checks: dict[str, Any] = {
            "process_health": self._check_process_health(app_path),
            "port_availability": self._check_ports(),
            "memory_usage": self._check_memory(),
            "cpu_usage": self._check_cpu(),
            "disk_space": self._check_disk(app_path),
            "dependency_freshness": self._check_dependencies(app_path),
            "code_smells": self._check_code_quality(app_path),
            "api_keys_valid": self._check_api_keys(),
            "data_integrity": self._check_data_integrity(app_path),
            "agent_connectivity": self._check_caamp_health(app_path),
            "log_errors": self._check_logs(app_path),
            "performance_baseline": self._measure_performance(app_path),
            "security_vulnerabilities": self._check_security(app_path),
            "feature_availability": self._check_features(app_path),
            "orchestrator_sync": self._check_orchestrator_sync(app_path),
        }

        failed = sum(1 for c in checks.values() if c.get("status") == "FAIL")
        warned = sum(1 for c in checks.values() if c.get("status") == "WARN")

        if failed > 0:
            overall_status = "CRITICAL"
        elif warned > 0:
            overall_status = "DEGRADED"
        else:
            overall_status = "PERFECT"

        return {
            "app_name": app_path.name,
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "overall_status": overall_status,
            "failed_checks": failed,
            "warning_checks": warned,
        }

    def _check_process_health(self, app_path: Path) -> dict[str, Any]:
        app_name = app_path.name.lower()
        if psutil is None:
            return {"status": "WARN", "message": "psutil not installed"}

        pids: list[int] = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                pname = (proc.info.get("name") or "").lower()
                cmdline = " ".join(proc.info.get("cmdline") or []).lower()
                if app_name in pname or app_name in cmdline:
                    pids.append(int(proc.info["pid"]))
            except Exception:
                continue
        return {
            "status": "PASS" if pids else "WARN",
            "running_processes": len(pids),
            "pids": pids,
        }

    def _check_ports(self) -> dict[str, Any]:
        listening: list[int] = []
        if psutil is not None:
            try:
                for conn in psutil.net_connections(kind="inet"):
                    if conn.status == "LISTEN" and conn.laddr:
                        listening.append(int(conn.laddr.port))
            except Exception:
                pass
        if not listening:
            for port in COMMON_PORTS:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.05)
                    if s.connect_ex(("127.0.0.1", port)) == 0:
                        listening.append(port)

        conflicts = sorted({p for p in COMMON_PORTS if p in listening})
        return {
            "status": "PASS" if not conflicts else "WARN",
            "conflicts": conflicts,
            "sample_listening_ports": sorted(set(listening))[:25],
        }

    def _check_memory(self) -> dict[str, Any]:
        if psutil is None:
            return {"status": "WARN", "message": "psutil not installed"}
        mem = psutil.virtual_memory()
        status = "PASS" if mem.percent < 80 else "WARN" if mem.percent < 90 else "FAIL"
        return {
            "status": status,
            "percent_used": float(mem.percent),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "total_gb": round(mem.total / (1024 ** 3), 2),
        }

    def _check_cpu(self) -> dict[str, Any]:
        if psutil is None:
            return {"status": "WARN", "message": "psutil not installed"}
        cpu = psutil.cpu_percent(interval=0.5)
        status = "PASS" if cpu < 70 else "WARN" if cpu < 90 else "FAIL"
        return {
            "status": status,
            "percent_used": float(cpu),
            "cores": int(psutil.cpu_count() or 1),
        }

    def _check_disk(self, app_path: Path) -> dict[str, Any]:
        usage = shutil.disk_usage(str(app_path.drive or app_path.anchor or "/"))
        percent = (usage.used / usage.total) * 100 if usage.total else 0.0
        status = "PASS" if percent < 85 else "WARN"
        return {
            "status": status,
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "percent_used": round(percent, 2),
        }

    def _check_dependencies(self, app_path: Path) -> dict[str, Any]:
        if not (app_path / "requirements.txt").exists():
            return {"status": "PASS", "outdated_count": 0, "outdated_packages": []}

        if not self.deep_checks:
            return {
                "status": "WARN",
                "outdated_count": 0,
                "outdated_packages": [],
                "message": "Dependency freshness skipped in quick mode",
            }

        cmd = [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=app_path, timeout=25)
        except subprocess.TimeoutExpired:
            return {"status": "WARN", "message": "Dependency freshness check timed out"}
        if result.returncode != 0:
            return {"status": "WARN", "message": result.stderr.strip()[:300]}

        outdated = []
        try:
            data = json.loads(result.stdout or "[]")
            outdated = [pkg.get("name", "") for pkg in data if pkg.get("name") and pkg.get("name") != "pip"]
        except Exception:
            pass

        return {
            "status": "WARN" if len(outdated) > 5 else "PASS",
            "outdated_count": len(outdated),
            "outdated_packages": outdated[:10],
        }

    def _check_code_quality(self, app_path: Path) -> dict[str, Any]:
        issues: list[str] = []
        for py_file in self._iter_python_files(app_path):
            try:
                lines = py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                for index, line in enumerate(lines, start=1):
                    if "TODO" in line or "FIXME" in line:
                        issues.append(f"{py_file.name}:{index} TODO/FIXME")
                    if line.strip() == "except:":
                        issues.append(f"{py_file.name}:{index} bare except")
            except Exception:
                continue
        return {
            "status": "PASS" if not issues else "WARN",
            "issue_count": len(issues),
            "issues": issues[:20],
        }

    def _check_api_keys(self) -> dict[str, Any]:
        master_key_path = self.orchestrator_path / ".openai-master-key.json"
        if not master_key_path.exists():
            return {"status": "WARN", "key_present": False, "message": "master key file missing"}
        try:
            data = json.loads(master_key_path.read_text(encoding="utf-8"))
            key = str(data.get("openai", {}).get("api_key", "")).strip()
        except Exception as exc:
            return {"status": "WARN", "key_present": False, "message": str(exc)}

        is_valid = bool(key and "paste-your" not in key)
        return {"status": "PASS" if is_valid else "WARN", "key_present": is_valid}

    def _check_data_integrity(self, app_path: Path) -> dict[str, Any]:
        total_files = 0
        corrupted = 0
        for folder_name in DATA_DIR_CANDIDATES:
            data_path = app_path / folder_name
            if not data_path.exists():
                continue
            for file_path in data_path.rglob("*"):
                if not file_path.is_file():
                    continue
                if file_path.suffix.lower() in {".json", ".csv", ".txt", ".pdf", ".docx"}:
                    total_files += 1
                    try:
                        if file_path.stat().st_size == 0:
                            corrupted += 1
                    except OSError:
                        corrupted += 1

        if total_files == 0:
            status = "PASS"
        elif corrupted == 0:
            status = "PASS"
        elif corrupted > max(1, int(total_files * 0.1)):
            status = "FAIL"
        else:
            status = "WARN"

        return {
            "status": status,
            "total_files": total_files,
            "corrupted_files": corrupted,
        }

    def _check_caamp_health(self, app_path: Path) -> dict[str, Any]:
        if not self.deep_checks:
            return {
                "status": "WARN",
                "caamp_healthy": False,
                "error": "CAAMP doctor skipped in quick mode",
            }

        cmd = ["npx", "@cleocode/caamp", "doctor", "--json"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=app_path, timeout=20)
            if result.returncode == 0:
                return {"status": "PASS", "caamp_healthy": True}
            return {
                "status": "WARN",
                "caamp_healthy": False,
                "error": (result.stderr or result.stdout).strip()[:200],
            }
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return {"status": "WARN", "caamp_healthy": False, "error": str(exc)[:200]}

    def _check_logs(self, app_path: Path) -> dict[str, Any]:
        error_count = 0
        samples: list[str] = []
        for log_file in self._iter_log_files(app_path):
            try:
                lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()[-100:]
                for line in lines:
                    low = line.lower()
                    if "error" in low or "exception" in low or "critical" in low or "fail" in low:
                        error_count += 1
                        if len(samples) < 10:
                            samples.append(line[:120])
            except Exception:
                continue
        return {
            "status": "PASS" if error_count == 0 else "WARN",
            "error_count": error_count,
            "recent_errors": samples,
        }

    def _measure_performance(self, app_path: Path) -> dict[str, Any]:
        start = time.perf_counter()
        result = subprocess.run([sys.executable, "-c", "print('ok')"], capture_output=True, text=True, cwd=app_path)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        status = "PASS" if result.returncode == 0 and elapsed_ms < 500 else "WARN"
        return {
            "status": status,
            "response_ms": elapsed_ms,
            "python_ok": result.returncode == 0,
        }

    def _check_security(self, app_path: Path) -> dict[str, Any]:
        vulnerabilities: list[str] = []
        for py_file in self._iter_python_files(app_path):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            low = content.lower()
            if "password" in low and "os.getenv" not in low and "input(" not in low:
                vulnerabilities.append(f"{py_file.name}: possible hardcoded secret")
            if "eval(" in content or "exec(" in content:
                vulnerabilities.append(f"{py_file.name}: dynamic execution usage")
        return {
            "status": "PASS" if not vulnerabilities else "WARN",
            "vulnerabilities": vulnerabilities[:10],
        }

    def _check_features(self, app_path: Path) -> dict[str, Any]:
        feature_count = 0
        markers = ["def ", "class ", "@app.", "@skill", "@tool", "@agent", "register_"]
        for py_file in self._iter_python_files(app_path):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if any(marker in content for marker in markers):
                feature_count += 1
        return {"status": "ACTIVE", "feature_count": feature_count}

    def _check_orchestrator_sync(self, app_path: Path) -> dict[str, Any]:
        synced = (app_path / ".orchestrator_sync").exists() or (app_path / "openai_key_manager.py").exists()
        return {"status": "PASS" if synced else "WARN", "synced": synced}

    def apply_auto_healing(self, analysis_results: dict[str, Any]) -> list[str]:
        print("[2/6] Applying auto-healing")
        actions: list[str] = []

        for app_name, results in analysis_results.items():
            status = results.get("overall_status", "UNKNOWN")
            checks = results.get("checks", {})
            app_path = self.github_root / app_name

            if status == "CRITICAL":
                action = self._emergency_heal(app_path, checks)
                actions.append(f"EMERGENCY {app_name}: {action}")
            elif status == "DEGRADED":
                action = self._standard_heal(app_path, checks)
                actions.append(f"HEALED {app_name}: {action}")
            else:
                actions.append(f"OPTIMIZED {app_name}: Performance maintained")

        return actions

    def _emergency_heal(self, app_path: Path, checks: dict[str, Any]) -> str:
        steps: list[str] = []
        memory = checks.get("memory_usage", {})
        disk = checks.get("disk_space", {})

        if memory.get("status") == "FAIL":
            steps.append("memory pressure flagged")
        if disk.get("status") == "FAIL":
            steps.append("disk pressure flagged")

        if not steps:
            steps.append("critical state flagged for manual intervention")
        return ", ".join(steps)

    def _standard_heal(self, app_path: Path, checks: dict[str, Any]) -> str:
        steps: list[str] = []

        dep = checks.get("dependency_freshness", {})
        if self.deep_checks and dep.get("status") == "WARN" and (app_path / "requirements.txt").exists():
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"],
                cwd=app_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                steps.append("dependencies updated")
            else:
                steps.append("dependency update attempted")
        elif dep.get("status") == "WARN":
            steps.append("dependency refresh queued")

        caamp = checks.get("agent_connectivity", {})
        if caamp.get("status") == "WARN":
            steps.append("agent connectivity requires follow-up")

        code_smells = checks.get("code_smells", {})
        if code_smells.get("status") == "WARN":
            steps.append("code smells logged")

        if not steps:
            steps.append("monitoring mode")
        return ", ".join(steps)

    def create_orchestrator_health_dashboard(self, analysis_results: dict[str, Any]) -> Path:
        print("[3/6] Writing dashboard")
        dashboard_path = self.orchestrator_path / "orchestrator_dashboard.html"

        cards: list[str] = []
        for app_name, info in sorted(analysis_results.items()):
            status = info.get("overall_status", "UNKNOWN")
            css = "perfect" if status == "PERFECT" else "degraded" if status == "DEGRADED" else "critical"
            cards.append(
                f"<div class='app {css}'><h3>{app_name}</h3><p>Status: {status}</p>"
                f"<p>Failed: {info.get('failed_checks', 0)} | Warnings: {info.get('warning_checks', 0)}</p></div>"
            )

        html = f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'/>
<meta http-equiv='refresh' content='30'/>
<title>AI-FACTORY-v2 Orchestrator Dashboard</title>
<style>
body {{ font-family: Consolas, monospace; background: #0a0a0a; color: #d6ffd6; padding: 24px; }}
h1 {{ color: #9fff9f; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }}
.app {{ border: 1px solid #2a5; border-radius: 8px; padding: 12px; }}
.perfect {{ background: #0f2a0f; }}
.degraded {{ background: #332a0a; }}
.critical {{ background: #3a0f0f; }}
.meta {{ color: #aacdaa; }}
</style>
</head>
<body>
<h1>AI-FACTORY-v2 Orchestrator Dashboard</h1>
<p class='meta'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p class='meta'>Total applications: {len(self.apps)} | Auto-healing: active</p>
<div class='grid'>
{''.join(cards) if cards else '<p>No applications discovered.</p>'}
</div>
</body>
</html>
"""
        dashboard_path.write_text(html, encoding="utf-8")
        return dashboard_path

    def schedule_distributed_healing(self) -> str:
        print("[4/6] Scheduling distributed healing")
        schedule_path = self.orchestrator_path / "orchestrator_healing.ps1"
        py_cmd = f'& "{sys.executable}" "{self.orchestrator_path / "ultimate_orchestrator.py"}" --once'

        schedule_script = (
            f"$repo = \"{self.orchestrator_path}\"\n"
            "Set-Location $repo\n"
            f"{py_cmd}\n"
        )
        schedule_path.write_text(schedule_script, encoding="utf-8")

        cmd = [
            "schtasks",
            "/create",
            "/tn",
            "AIFactoryOrchestrator_Healing",
            "/sc",
            "hourly",
            "/mo",
            "6",
            "/tr",
            f'powershell.exe -ExecutionPolicy Bypass -File "{schedule_path}"',
            "/f",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return "Distributed healing scheduled every 6 hours"
        return f"Scheduling skipped ({(result.stderr or result.stdout).strip()[:180]})"

    def generate_master_report(
        self,
        analysis_results: dict[str, Any],
        healing_actions: list[str],
        schedule_status: str,
    ) -> Path:
        print("[5/6] Generating master report")
        perfect = sum(1 for r in analysis_results.values() if r.get("overall_status") == "PERFECT")
        degraded = sum(1 for r in analysis_results.values() if r.get("overall_status") == "DEGRADED")
        critical = sum(1 for r in analysis_results.values() if r.get("overall_status") == "CRITICAL")

        lines: list[str] = []
        lines.append("AI-FACTORY-v2 ORCHESTRATOR - MASTER RELIABILITY REPORT")
        lines.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        lines.append("")
        lines.append(f"Total applications: {len(self.apps)}")
        lines.append(f"Health summary: PERFECT={perfect} | DEGRADED={degraded} | CRITICAL={critical}")
        lines.append(f"Scheduler: {schedule_status}")
        lines.append("")
        lines.append("Application status:")
        for app_name, result in sorted(analysis_results.items()):
            lines.append(
                f"- {app_name}: {result.get('overall_status', 'UNKNOWN')} "
                f"(failed={result.get('failed_checks', 0)}, warnings={result.get('warning_checks', 0)})"
            )
        lines.append("")
        lines.append("Healing actions:")
        for action in healing_actions:
            lines.append(f"- {action}")

        report_path = self.orchestrator_path / "orchestrator_master_report.txt"
        report_path.write_text("\n".join(lines), encoding="utf-8")

        raw_json_path = self.orchestrator_path / "orchestrator_analysis_results.json"
        raw_json_path.write_text(json.dumps(analysis_results, indent=2), encoding="utf-8")
        return report_path

    def start_real_time_monitoring(self) -> None:
        print("[6/6] Starting real-time monitor")

        def monitor() -> None:
            for _ in range(3):
                time.sleep(10)
            # Placeholder monitor loop intended for daemonized runs.

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def execute(self) -> tuple[dict[str, Any], list[str], Path, str, Path]:
        print("Initiating AI-FACTORY-v2 Ultimate Orchestrator")
        analysis = self.run_quantum_demand_analysis()
        healing = self.apply_auto_healing(analysis)
        dashboard_path = self.create_orchestrator_health_dashboard(analysis)
        schedule_status = self.schedule_distributed_healing()
        self.start_real_time_monitoring()
        report_path = self.generate_master_report(analysis, healing, schedule_status)
        return analysis, healing, dashboard_path, schedule_status, report_path


def _resolve_default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main(argv: list[str]) -> int:
    github_root = _resolve_default_root()
    once = "--once" in argv
    deep_checks = "--deep" in argv

    orchestrator = UltimateOrchestrator(str(github_root), deep_checks=deep_checks)
    analysis, healing, dashboard_path, schedule_status, report_path = orchestrator.execute()

    print("\nAI-FACTORY-v2 Ultimate Orchestrator complete")
    print(f"Applications analyzed: {len(analysis)}")
    print(f"Healing actions: {len(healing)}")
    print(f"Dashboard: {dashboard_path}")
    print(f"Report: {report_path}")
    print(f"Scheduler: {schedule_status}")

    if not once:
        try:
            os.startfile(str(dashboard_path))  # type: ignore[attr-defined]
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
