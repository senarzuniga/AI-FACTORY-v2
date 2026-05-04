#!/usr/bin/env python3
"""Autonomous Cascade Orchestrator with self-learning and controlled deployment."""

from __future__ import annotations

import argparse
import asyncio
import ast
import hashlib
import json
import os
import re
import subprocess
import traceback
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

import numpy as np


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LEARNING_DIR = DATA_DIR / "learning"
LOG_DIR = ROOT / "logs"


class CascadePhase(str, Enum):
    TRIGGER_RECEIVED = "trigger_received"
    PLANNING = "planning"
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    VALIDATION = "validation"
    LEARNING = "learning"
    DEPLOYMENT = "deployment"
    COMPLETE = "complete"


class AgentRole(str, Enum):
    ANALYZER = "analyzer"
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    DEPLOYER = "deployer"
    LEARNER = "learner"
    EVOLVER = "evolver"


@dataclass
class CascadeContext:
    id: str
    trigger: str
    started_at: datetime
    phase: CascadePhase
    agents_activated: List[str] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    learning_data: Dict[str, Any] = field(default_factory=dict)
    deployed_features: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentCapability:
    name: str
    role: AgentRole
    input_types: List[str]
    output_types: List[str]
    performance_score: float = 1.0
    last_used: datetime = field(default_factory=lambda: datetime.now(UTC))
    success_rate: float = 1.0
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)


class CascadeEventBus:
    def __init__(self, log_file: Path | None = None) -> None:
        self.handlers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = defaultdict(list)
        self.event_history: List[Dict[str, Any]] = []
        self.log_file = log_file or (LOG_DIR / "cascade.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def on(
        self,
        event_type: str,
        handler: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    ):
        if handler is not None:
            self.handlers[event_type].append(handler)
            return handler

        def decorator(func: Callable[[Dict[str, Any]], Awaitable[None]]):
            self.handlers[event_type].append(func)
            return func

        return decorator

    async def emit(self, event_type: str, data: Dict[str, Any]) -> str:
        event_id = hashlib.md5(f"{event_type}:{datetime.now(UTC).isoformat()}".encode("utf-8")).hexdigest()[:10]
        event = {
            "id": event_id,
            "type": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "data": data,
        }
        self.event_history.append(event)
        self._write_log_line(event)

        handlers = self.handlers.get(event_type, [])
        if handlers:
            outcomes = await asyncio.gather(*(h(event) for h in handlers), return_exceptions=True)
            for outcome in outcomes:
                if isinstance(outcome, Exception):
                    self._write_log_line(
                        {
                            "id": hashlib.md5(str(outcome).encode("utf-8")).hexdigest()[:10],
                            "type": "event_handler_error",
                            "timestamp": datetime.now(UTC).isoformat(),
                            "data": {"event_type": event_type, "error": repr(outcome)},
                        }
                    )
        return event_id

    def _write_log_line(self, event: Dict[str, Any]) -> None:
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


class CascadePlanner:
    def __init__(self) -> None:
        self.template_path = DATA_DIR / "workflow_templates.json"
        self.learning_path = LEARNING_DIR / "learning_data.json"
        self.workflow_templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        if self.template_path.exists():
            return json.loads(self.template_path.read_text(encoding="utf-8"))
        return {
            "code_improvement": {
                "cascade": [
                    {"phase": "analysis", "agents": ["code_analyzer", "requirement_analyzer"], "parallel": True},
                    {"phase": "execution", "agents": ["code_generator"], "parallel": False},
                    {"phase": "validation", "agents": ["reviewer", "tester"], "parallel": True},
                ]
            },
            "bug_fix": {
                "cascade": [
                    {"phase": "analysis", "agents": ["code_analyzer"], "parallel": False},
                    {"phase": "execution", "agents": ["code_generator"], "parallel": False},
                    {"phase": "validation", "agents": ["tester"], "parallel": False},
                ]
            },
            "feature_addition": {
                "cascade": [
                    {"phase": "analysis", "agents": ["requirement_analyzer", "code_analyzer"], "parallel": True},
                    {"phase": "execution", "agents": ["code_generator"], "parallel": False},
                    {"phase": "validation", "agents": ["reviewer", "tester"], "parallel": True},
                ]
            },
        }

    async def create_cascade(self, trigger: str, context: Dict[str, Any]) -> Dict[str, Any]:
        trigger_type = self._classify_trigger(trigger)
        base = self.workflow_templates.get(trigger_type, self.workflow_templates["code_improvement"])
        enhanced = self._enhance_with_learning(base, trigger_type)
        optimized = self._optimize(enhanced)
        return {
            "trigger_type": trigger_type,
            "cascade": optimized["cascade"],
            "estimated_duration": self._estimate_duration(optimized["cascade"]),
            "parallel_batches": self._create_batches(optimized["cascade"]),
            "context_hints": context,
        }

    def _classify_trigger(self, trigger: str) -> str:
        lower = trigger.lower()
        if any(w in lower for w in ["bug", "fix", "error", "crash", "falla"]):
            return "bug_fix"
        if any(w in lower for w in ["feature", "new", "implement", "add", "agregar"]):
            return "feature_addition"
        return "code_improvement"

    def _enhance_with_learning(self, template: Dict[str, Any], trigger_type: str) -> Dict[str, Any]:
        enhanced = json.loads(json.dumps(template))
        if not self.learning_path.exists():
            return enhanced

        learning = json.loads(self.learning_path.read_text(encoding="utf-8"))
        optimizations = learning.get("workflow_optimizations", [])
        for opt in optimizations:
            if opt.get("trigger_type") == trigger_type and opt.get("confidence", 0.0) >= 0.65:
                preferred = set(opt.get("optimal_agents", []))
                for phase in enhanced.get("cascade", []):
                    phase["agents"] = sorted(set(phase.get("agents", [])) | preferred)
        return enhanced

    def _optimize(self, template: Dict[str, Any]) -> Dict[str, Any]:
        out = json.loads(json.dumps(template))
        for phase in out.get("cascade", []):
            agents = phase.get("agents", [])
            if len(agents) <= 1:
                phase["parallel"] = False
            else:
                phase["parallel"] = phase.get("parallel", True)
        return out

    def _create_batches(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"type": "parallel" if p.get("parallel") else "sequential", "batch": [p]} for p in phases]

    def _estimate_duration(self, phases: List[Dict[str, Any]]) -> float:
        baseline = 2.5
        total = 0.0
        for phase in phases:
            n = max(1, len(phase.get("agents", [])))
            total += baseline if not phase.get("parallel") else (baseline / min(n, 3))
        return round(total, 2)


class IntelligentAgentPool:
    def __init__(self) -> None:
        self.agents: Dict[str, Any] = {}
        self.capabilities: Dict[str, AgentCapability] = {}
        self.execution_durations: Dict[str, List[float]] = defaultdict(list)
        self.success_flags: Dict[str, List[float]] = defaultdict(list)
        self.evolution_log: List[Dict[str, Any]] = []

    def register_agent(
        self,
        name: str,
        agent_instance: Any,
        role: AgentRole,
        input_types: List[str],
        output_types: List[str],
    ) -> None:
        self.agents[name] = agent_instance
        self.capabilities[name] = AgentCapability(
            name=name,
            role=role,
            input_types=input_types,
            output_types=output_types,
        )

    async def execute_agent(self, name: str, input_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        start = datetime.now(UTC)
        if name not in self.agents:
            raise ValueError(f"Agent not registered: {name}")
        timeout_s = float(context.get("agent_timeout_seconds", 60.0))
        try:
            result = await asyncio.wait_for(self.agents[name].execute(input_data, context), timeout=timeout_s)
            duration = (datetime.now(UTC) - start).total_seconds()
            self._update_performance(name, duration=duration, success=True)
            return result
        except Exception:
            duration = (datetime.now(UTC) - start).total_seconds()
            self._update_performance(name, duration=duration, success=False)
            raise

    def _update_performance(self, name: str, duration: float, success: bool) -> None:
        cap = self.capabilities[name]
        self.execution_durations[name].append(duration)
        self.success_flags[name].append(1.0 if success else 0.0)

        self.execution_durations[name] = self.execution_durations[name][-100:]
        self.success_flags[name] = self.success_flags[name][-100:]

        cap.last_used = datetime.now(UTC)
        cap.success_rate = float(np.mean(self.success_flags[name])) if self.success_flags[name] else 0.0

        avg_duration = float(np.mean(self.execution_durations[name])) if self.execution_durations[name] else 60.0
        speed_score = min(1.0, 20.0 / max(avg_duration, 1e-6))
        cap.performance_score = round((cap.success_rate * 0.7) + (speed_score * 0.3), 4)

    def get_best_agent_for_task(self, output_type: str) -> Optional[str]:
        scored: List[tuple[float, str]] = []
        now = datetime.now(UTC)
        for name, cap in self.capabilities.items():
            if output_type not in cap.output_types:
                continue
            age_h = max((now - cap.last_used).total_seconds() / 3600.0, 0.0)
            recency = 1.0 / (1.0 + age_h)
            scored.append((cap.performance_score * recency, name))
        if not scored:
            return None
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    async def evolve_agents(self, learning_data: Dict[str, Any]) -> None:
        for name, cap in self.capabilities.items():
            changes: Dict[str, Any] = {}
            if cap.success_rate < 0.70:
                changes["timeout_multiplier"] = 1.5
                changes["retry_boost"] = 1
            if cap.performance_score < 0.60:
                changes["add_reflection"] = True
            if not changes:
                continue
            agent = self.agents[name]
            if hasattr(agent, "evolve"):
                await agent.evolve(changes)
                cap.evolution_history.append(changes)
                self.evolution_log.append({"agent": name, "changes": changes, "timestamp": datetime.now(UTC).isoformat()})


class SelfLearningEngine:
    def __init__(self, event_bus: CascadeEventBus) -> None:
        self.event_bus = event_bus
        self.learning_path = LEARNING_DIR / "learning_data.json"
        LEARNING_DIR.mkdir(parents=True, exist_ok=True)
        self.learning_data = self._load_learning()
        self._register_listeners()

    def _load_learning(self) -> Dict[str, Any]:
        if self.learning_path.exists():
            return json.loads(self.learning_path.read_text(encoding="utf-8"))
        return {
            "successful_patterns": [],
            "failure_patterns": [],
            "performance_metrics": {},
            "workflow_optimizations": [],
        }

    def _register_listeners(self) -> None:
        self.event_bus.on("cascade_complete", self._on_cascade_complete)
        self.event_bus.on("cascade_failed", self._on_cascade_failed)
        self.event_bus.on("agent.completed", self._on_agent_output)

    async def _on_cascade_complete(self, event: Dict[str, Any]) -> None:
        data = event.get("data", {})
        self.learning_data["successful_patterns"].append(
            {
                "trigger_type": data.get("trigger_type", "unknown"),
                "agent_sequence": data.get("agents_used", []),
                "duration": data.get("duration", 0.0),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        self.learning_data["successful_patterns"] = self.learning_data["successful_patterns"][-200:]
        await self.optimize_workflows()
        self._persist()

    async def _on_cascade_failed(self, event: Dict[str, Any]) -> None:
        data = event.get("data", {})
        self.learning_data["failure_patterns"].append(
            {
                "trigger_type": data.get("trigger_type", "unknown"),
                "failed_agent": data.get("failed_agent"),
                "error_type": data.get("error", {}).get("type", "unknown"),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        self.learning_data["failure_patterns"] = self.learning_data["failure_patterns"][-200:]
        self._persist()

    async def _on_agent_output(self, event: Dict[str, Any]) -> None:
        data = event.get("data", {})
        name = data.get("agent")
        if not name:
            return
        m = self.learning_data["performance_metrics"].setdefault(name, {"durations": [], "runs": 0})
        m["durations"].append(float(data.get("duration", 0.0)))
        m["durations"] = m["durations"][-100:]
        m["runs"] += 1
        self._persist()

    async def optimize_workflows(self) -> None:
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for p in self.learning_data.get("successful_patterns", []):
            grouped[str(p.get("trigger_type", "unknown"))].append(p)

        optimizations: List[Dict[str, Any]] = []
        for trigger_type, patterns in grouped.items():
            if len(patterns) < 3:
                continue
            durations = [float(p.get("duration", 0.0)) for p in patterns if p.get("duration") is not None]
            avg_duration = float(np.mean(durations)) if durations else 0.0
            all_agents = [a for p in patterns for a in p.get("agent_sequence", [])]
            common = [x for x, _ in Counter(all_agents).most_common(5)]
            confidence = min(0.95, len(patterns) / 20.0)
            optimizations.append(
                {
                    "trigger_type": trigger_type,
                    "optimal_agents": common,
                    "expected_duration": round(avg_duration, 3),
                    "confidence": round(confidence, 3),
                }
            )
        self.learning_data["workflow_optimizations"] = optimizations

    def _persist(self) -> None:
        self.learning_path.write_text(json.dumps(self.learning_data, indent=2, ensure_ascii=False), encoding="utf-8")


class AutoDeploymentEngine:
    def __init__(self, event_bus: CascadeEventBus, repo_path: Path, enable_git_deploy: bool = False, allow_push: bool = False) -> None:
        self.event_bus = event_bus
        self.repo_path = repo_path
        self.enable_git_deploy = enable_git_deploy
        self.allow_push = allow_push
        self.history: List[Dict[str, Any]] = []
        self.linked_apps_file = ROOT / "config" / "linked_apps.json"

    async def deploy_feature(self, feature: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        deployment_id = hashlib.md5(f"{feature.get('name','feature')}:{datetime.now(UTC).isoformat()}".encode("utf-8")).hexdigest()[:12]

        if not self.enable_git_deploy:
            linked = await self._deploy_linked_apps(context)
            result = {
                "deployment_id": deployment_id,
                "feature": feature,
                "status": "dry_run",
                "message": "Git deployment disabled. Enable with --enable-git-deploy.",
                "linked_apps": linked,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            self.history.append(result)
            await self.event_bus.emit("deployment_complete", result)
            return result

        try:
            branch = f"auto/cascade-{deployment_id}"
            self._run_git(["checkout", "-b", branch])

            changed_files = self._apply_feature_changes(feature)
            self._run_git(["add", *changed_files])
            self._run_git(["commit", "-m", f"feat(cascade): auto deploy {feature.get('name','feature')}"])

            if self.allow_push:
                self._run_git(["push", "-u", "origin", branch])

            linked = await self._deploy_linked_apps(context)
            result = {
                "deployment_id": deployment_id,
                "feature": feature,
                "status": "deployed",
                "branch": branch,
                "changed_files": changed_files,
                "linked_apps": linked,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            self.history.append(result)
            await self.event_bus.emit("deployment_complete", result)
            return result
        except Exception as exc:
            result = {
                "deployment_id": deployment_id,
                "feature": feature,
                "status": "failed",
                "error": str(exc),
                "timestamp": datetime.now(UTC).isoformat(),
            }
            self.history.append(result)
            await self.event_bus.emit("deployment_complete", result)
            return result

    def _run_git(self, args: List[str]) -> None:
        subprocess.run(["git", *args], cwd=self.repo_path, check=True, capture_output=True, text=True)

    def _apply_feature_changes(self, feature: Dict[str, Any]) -> List[str]:
        files: List[str] = []
        for change in feature.get("file_changes", []):
            rel_path = str(change.get("path", "")).strip().replace("\\", "/")
            if not rel_path:
                continue
            if not rel_path.startswith("generated/"):
                rel_path = f"generated/{rel_path}"
            target = self.repo_path / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(change.get("content", ""), encoding="utf-8")
            files.append(rel_path)
        return files

    async def _deploy_linked_apps(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not context.get("enable_linked_deploy", False):
            return [{"status": "skipped", "reason": "enable_linked_deploy=false"}]

        if not self.linked_apps_file.exists():
            return [{"status": "skipped", "reason": "missing linked_apps.json"}]

        payload = json.loads(self.linked_apps_file.read_text(encoding="utf-8"))
        apps = payload.get("apps", [])
        results: List[Dict[str, Any]] = []
        for app in apps:
            command = app.get("deploy_command")
            if not command:
                results.append({"app": app.get("name", "unknown"), "status": "skipped", "reason": "no command"})
                continue
            try:
                proc = subprocess.run(command, cwd=self.repo_path, shell=True, capture_output=True, text=True, timeout=180)
                results.append(
                    {
                        "app": app.get("name", "unknown"),
                        "status": "ok" if proc.returncode == 0 else "failed",
                        "code": proc.returncode,
                        "stdout": proc.stdout[-5000:],
                        "stderr": proc.stderr[-5000:],
                    }
                )
            except Exception as exc:
                results.append({"app": app.get("name", "unknown"), "status": "failed", "error": str(exc)})
        return results


class SelfLearningCodeAnalyzer:
    def __init__(self) -> None:
        self.knowledge_file = LEARNING_DIR / "analyzer_knowledge.json"
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self) -> Dict[str, Any]:
        if self.knowledge_file.exists():
            return json.loads(self.knowledge_file.read_text(encoding="utf-8"))
        return {"patterns": [{"regex": r"TODO|FIXME", "type": "todo_marker", "severity": "low"}]}

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        trigger = input_data.get("trigger", "")
        target_code = input_data.get("code", "")

        if not target_code:
            for p in context.get("candidate_files", ["main.py"]):
                fp = ROOT / p
                if fp.exists() and fp.is_file() and fp.suffix == ".py":
                    target_code = fp.read_text(encoding="utf-8", errors="ignore")
                    break

        complexity = self._complexity(target_code)
        issues = self._issues(target_code)
        patterns = self._detect_patterns(target_code)
        suggestions = self._suggest(complexity, trigger)

        return {
            "complexity": complexity,
            "issues": issues,
            "patterns": patterns,
            "suggestions": suggestions,
            "summary": f"Detected {len(issues)} issue candidates",
        }

    def _complexity(self, code: str) -> float:
        tokens = re.findall(r"\b(if|for|while|and|or|except|match|case)\b", code)
        lines = max(1, len(code.splitlines()))
        return round(len(tokens) / lines, 4)

    def _issues(self, code: str) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        for p in self.knowledge.get("patterns", []):
            regex = p.get("regex", "")
            if regex and re.search(regex, code):
                issues.append({"type": p.get("type", "pattern"), "severity": p.get("severity", "medium")})
        return issues

    def _detect_patterns(self, code: str) -> List[str]:
        out: List[str] = []
        if "async def" in code:
            out.append("async")
        if "class " in code:
            out.append("oop")
        if "dataclass" in code:
            out.append("dataclass")
        return out

    def _suggest(self, complexity: float, trigger: str) -> List[str]:
        suggestions: List[str] = []
        if complexity > 0.2:
            suggestions.append("Split complex logic into smaller units")
        if "security" in trigger.lower():
            suggestions.append("Add stronger validation and sanitization")
        if not suggestions:
            suggestions.append("Add targeted tests for changed behavior")
        return suggestions

    async def evolve(self, improvements: Dict[str, Any]) -> None:
        if improvements.get("add_reflection"):
            self.knowledge.setdefault("patterns", []).append(
                {"regex": r"except\s*:\s*pass", "type": "silent_exception", "severity": "high"}
            )
        self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)
        self.knowledge_file.write_text(json.dumps(self.knowledge, indent=2, ensure_ascii=False), encoding="utf-8")


class RequirementAnalyzer:
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        trigger = str(input_data.get("trigger", "")).strip()
        high_priority = any(w in trigger.lower() for w in ["urgent", "critical", "security", "prod"])
        tags = [w for w in ["feature", "bug", "performance", "security"] if w in trigger.lower()]
        return {
            "requirements": trigger,
            "priority": "high" if high_priority else "normal",
            "tags": tags or ["improvement"],
            "constraints": context.get("constraints", {}),
        }


class CascadeCodeGenerator:
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        analysis = input_data.get("analysis", {})
        req = input_data.get("requirements", "No explicit requirements")
        suggestions = analysis.get("suggestions", []) if isinstance(analysis, dict) else []

        code = (
            '"""Auto-generated improvement from Cascade Orchestrator."""\n\n'
            "def apply_improvement(payload: dict) -> dict:\n"
            "    result = {\"status\": \"ok\", \"notes\": []}\n"
            f"    result['notes'].append('Requirement: {req}')\n"
            f"    result['notes'].append('Suggestion count: {len(suggestions)}')\n"
            "    return result\n"
        )

        quality = 0.9 if "pass" not in code else 0.6
        return {
            "code": code,
            "quality_score": quality,
            "validation": {"valid": self._is_valid_python(code), "errors": []},
        }

    def _is_valid_python(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    async def evolve(self, improvements: Dict[str, Any]) -> None:
        _ = improvements


class CascadeReviewer:
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        generated = str(input_data.get("generated_code", ""))
        issues: List[str] = []
        if "eval(" in generated:
            issues.append("Avoid eval")
        if "TODO" in generated:
            issues.append("Resolve TODO before deployment")
        score = 1.0 - (0.2 * len(issues))
        return {"review_issues": issues, "quality_score": max(0.0, min(1.0, score))}


class CascadeTester:
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        generated = str(input_data.get("generated_code", ""))
        valid = True
        errors: List[str] = []
        try:
            ast.parse(generated)
        except SyntaxError as exc:
            valid = False
            errors.append(str(exc))
        return {
            "validation": {"valid": valid, "errors": errors},
            "quality_score": 1.0 if valid else 0.2,
        }


class CascadeOrchestrator:
    def __init__(self, repo_path: Path = ROOT, enable_git_deploy: bool = False, allow_push: bool = False) -> None:
        self.repo_path = repo_path
        self.event_bus = CascadeEventBus()
        self.agent_pool = IntelligentAgentPool()
        self.planner = CascadePlanner()
        self.learning = SelfLearningEngine(self.event_bus)
        self.deployment = AutoDeploymentEngine(self.event_bus, repo_path=repo_path, enable_git_deploy=enable_git_deploy, allow_push=allow_push)

        self.active_cascades: Dict[str, asyncio.Task[Any]] = {}
        self.results: Dict[str, Dict[str, Any]] = {}
        self._register_agents()

    def _register_agents(self) -> None:
        self.agent_pool.register_agent("code_analyzer", SelfLearningCodeAnalyzer(), AgentRole.ANALYZER, ["code"], ["analysis"])
        self.agent_pool.register_agent("requirement_analyzer", RequirementAnalyzer(), AgentRole.PLANNER, ["trigger"], ["requirements"])
        self.agent_pool.register_agent("code_generator", CascadeCodeGenerator(), AgentRole.CODER, ["analysis", "requirements"], ["generated_code"])
        self.agent_pool.register_agent("reviewer", CascadeReviewer(), AgentRole.REVIEWER, ["generated_code"], ["review"])
        self.agent_pool.register_agent("tester", CascadeTester(), AgentRole.TESTER, ["generated_code"], ["tests"])

    async def trigger(self, trigger: str, context: Optional[Dict[str, Any]] = None) -> str:
        context = context or {}
        cascade_id = hashlib.md5(f"{trigger}:{datetime.now(UTC).isoformat()}".encode("utf-8")).hexdigest()[:16]
        cascade = CascadeContext(
            id=cascade_id,
            trigger=trigger,
            started_at=datetime.now(UTC),
            phase=CascadePhase.TRIGGER_RECEIVED,
        )
        await self.event_bus.emit("cascade_started", {"cascade_id": cascade.id, "trigger": trigger})
        task = asyncio.create_task(self._execute(cascade, context))
        self.active_cascades[cascade_id] = task
        return cascade_id

    async def _execute(self, cascade: CascadeContext, context: Dict[str, Any]) -> None:
        try:
            cascade.phase = CascadePhase.PLANNING
            plan = await self.planner.create_cascade(cascade.trigger, context)
            cascade.outputs["plan"] = plan

            for phase_block in plan.get("cascade", []):
                await self._execute_phase(cascade, phase_block, context)

            cascade.phase = CascadePhase.VALIDATION
            validation = await self._validate(cascade)
            cascade.outputs["final_validation"] = validation

            cascade.phase = CascadePhase.LEARNING
            await self.learning.optimize_workflows()
            await self.agent_pool.evolve_agents(self.learning.learning_data)

            if validation.get("ready_for_deployment", False):
                cascade.phase = CascadePhase.DEPLOYMENT
                deployed = await self._deploy(cascade, context)
                cascade.deployed_features.extend(deployed)

            cascade.phase = CascadePhase.COMPLETE
            duration = (datetime.now(UTC) - cascade.started_at).total_seconds()
            cascade.metrics["duration_seconds"] = duration
            self.results[cascade.id] = {"status": "success", "cascade": cascade}
            await self.event_bus.emit(
                "cascade_complete",
                {
                    "cascade_id": cascade.id,
                    "trigger_type": plan.get("trigger_type"),
                    "duration": duration,
                    "agents_used": cascade.agents_activated,
                    "deployed_features": cascade.deployed_features,
                },
            )
            self._persist_result(cascade.id)
        except Exception as exc:
            cascade.errors.append({"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
            self.results[cascade.id] = {"status": "failed", "cascade": cascade, "error": str(exc)}
            await self.event_bus.emit(
                "cascade_failed",
                {
                    "cascade_id": cascade.id,
                    "trigger_type": self.planner._classify_trigger(cascade.trigger),
                    "failed_agent": cascade.agents_activated[-1] if cascade.agents_activated else None,
                    "error": {"type": type(exc).__name__, "message": str(exc)},
                },
            )
            self._persist_result(cascade.id)
        finally:
            self.active_cascades.pop(cascade.id, None)

    async def _execute_phase(self, cascade: CascadeContext, phase: Dict[str, Any], context: Dict[str, Any]) -> None:
        phase_name = phase.get("phase", "unknown")
        agents = list(phase.get("agents", []))
        parallel = bool(phase.get("parallel", False))

        if parallel:
            results = await asyncio.gather(*(self._execute_agent(cascade, a, phase_name, context) for a in agents), return_exceptions=True)
            for name, result in zip(agents, results):
                if isinstance(result, Exception):
                    cascade.errors.append({"phase": phase_name, "agent": name, "error": str(result)})
                else:
                    cascade.outputs[f"{phase_name}.{name}"] = result
        else:
            for agent in agents:
                result = await self._execute_agent(cascade, agent, phase_name, context)
                cascade.outputs[f"{phase_name}.{agent}"] = result

        await self.event_bus.emit("cascade.phase_complete", {"cascade_id": cascade.id, "phase": phase_name})

    async def _execute_agent(self, cascade: CascadeContext, agent_name: str, phase_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._build_agent_input(cascade, phase_name)
        await self.event_bus.emit("agent_started", {"cascade_id": cascade.id, "agent": agent_name, "phase": phase_name})
        start = datetime.now(UTC)
        try:
            result = await self.agent_pool.execute_agent(agent_name, payload, context)
            duration = (datetime.now(UTC) - start).total_seconds()
            cascade.agents_activated.append(agent_name)
            await self.event_bus.emit(
                "agent.completed",
                {
                    "cascade_id": cascade.id,
                    "agent": agent_name,
                    "phase": phase_name,
                    "duration": duration,
                    "output": result,
                },
            )
            return result
        except Exception as exc:
            await self.event_bus.emit(
                "agent.failed",
                {
                    "cascade_id": cascade.id,
                    "agent": agent_name,
                    "phase": phase_name,
                    "error": str(exc),
                },
            )
            raise

    def _build_agent_input(self, cascade: CascadeContext, phase_name: str) -> Dict[str, Any]:
        analysis = cascade.outputs.get("analysis.code_analyzer", {})
        requirements = cascade.outputs.get("analysis.requirement_analyzer", {}).get("requirements", cascade.trigger)
        generated_code = cascade.outputs.get("execution.code_generator", {}).get("code", "")
        return {
            "cascade_id": cascade.id,
            "trigger": cascade.trigger,
            "phase": phase_name,
            "analysis": analysis,
            "requirements": requirements,
            "generated_code": generated_code,
            "previous_outputs": cascade.outputs,
        }

    async def _validate(self, cascade: CascadeContext) -> Dict[str, Any]:
        quality_values: List[float] = []
        issues: List[str] = []

        for key, out in cascade.outputs.items():
            if isinstance(out, dict) and "quality_score" in out:
                quality_values.append(float(out["quality_score"]))
            if isinstance(out, dict) and out.get("validation") and not out["validation"].get("valid", True):
                issues.append(f"Validation failed in {key}")

        quality = float(np.mean(quality_values)) if quality_values else 0.0
        ready = quality >= 0.80 and not issues
        return {
            "passed": not issues,
            "issues": issues,
            "quality_score": round(quality, 4),
            "ready_for_deployment": ready,
        }

    async def _deploy(self, cascade: CascadeContext, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        generated = cascade.outputs.get("execution.code_generator", {})
        if not isinstance(generated, dict) or "code" not in generated:
            return []

        feature = {
            "name": f"cascade_{cascade.id[:8]}",
            "confidence": generated.get("quality_score", 0.0),
            "file_changes": [
                {
                    "path": f"generated/cascade_{cascade.id[:8]}.py",
                    "content": generated["code"],
                }
            ],
        }
        deployment = await self.deployment.deploy_feature(feature, context)
        return [deployment]

    async def get_status(self, cascade_id: str) -> str:
        if cascade_id in self.active_cascades:
            return "running"
        if cascade_id in self.results:
            return self.results[cascade_id]["status"]
        return "not_found"

    async def get_result(self, cascade_id: str) -> Optional[Dict[str, Any]]:
        return self.results.get(cascade_id)

    def _persist_result(self, cascade_id: str) -> None:
        LEARNING_DIR.mkdir(parents=True, exist_ok=True)
        result_file = LEARNING_DIR / "cascade_results.json"
        payload: Dict[str, Any] = {}
        if result_file.exists():
            payload = json.loads(result_file.read_text(encoding="utf-8"))

        value = self.results[cascade_id]
        cascade: CascadeContext = value["cascade"]
        payload[cascade_id] = {
            "status": value["status"],
            "trigger": cascade.trigger,
            "started_at": cascade.started_at.isoformat(),
            "phase": cascade.phase.value,
            "agents": cascade.agents_activated,
            "outputs": list(cascade.outputs.keys()),
            "deployed_features": cascade.deployed_features,
            "errors": cascade.errors,
            "duration_seconds": cascade.metrics.get("duration_seconds", 0.0),
        }
        result_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _parse_context(raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return value
        return {"value": value}
    except json.JSONDecodeError:
        return {"raw_context": raw}


def _print_learning_summary() -> int:
    learning_file = LEARNING_DIR / "learning_data.json"
    if not learning_file.exists():
        print("No learning data found.")
        return 0

    payload = json.loads(learning_file.read_text(encoding="utf-8"))
    print("Learning Summary")
    print("- successful_patterns:", len(payload.get("successful_patterns", [])))
    print("- failure_patterns:", len(payload.get("failure_patterns", [])))
    print("- workflow_optimizations:", len(payload.get("workflow_optimizations", [])))
    print("- tracked_agents:", len(payload.get("performance_metrics", {})))
    return 0


def _print_result_status(cascade_id: Optional[str]) -> int:
    result_file = LEARNING_DIR / "cascade_results.json"
    if not result_file.exists():
        print("No cascade results found.")
        return 0
    payload = json.loads(result_file.read_text(encoding="utf-8"))
    if cascade_id:
        item = payload.get(cascade_id)
        if not item:
            print(f"Cascade {cascade_id} not found")
            return 1
        print(json.dumps(item, indent=2, ensure_ascii=False))
        return 0

    print("Latest Cascades")
    for key in list(payload.keys())[-10:]:
        v = payload[key]
        print(f"- {key}: {v.get('status')} phase={v.get('phase')} duration={v.get('duration_seconds', 0):.2f}s")
    return 0


async def run_cli_async(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Autonomous Cascade Orchestrator")
    parser.add_argument("trigger", nargs="?", help="Natural language trigger for cascade")
    parser.add_argument("--context", default=None, help="JSON context string")
    parser.add_argument("--status", nargs="?", const="", default=None, help="Show saved status (optionally for a cascade id)")
    parser.add_argument("--learn", action="store_true", help="Show learning summary")
    parser.add_argument("--repo-path", default=str(ROOT), help="Repository path")
    parser.add_argument("--enable-git-deploy", action="store_true", help="Enable git branch/commit deployment")
    parser.add_argument("--allow-push", action="store_true", help="Allow git push during deployment")
    parser.add_argument("--enable-linked-deploy", action="store_true", help="Enable deployment hooks to linked apps")

    args = parser.parse_args(argv)

    if args.learn:
        return _print_learning_summary()

    if args.status is not None:
        cid = args.status.strip() or None
        return _print_result_status(cid)

    if not args.trigger:
        parser.print_help()
        return 1

    context = _parse_context(args.context)
    context["enable_linked_deploy"] = bool(args.enable_linked_deploy)

    orchestrator = CascadeOrchestrator(
        repo_path=Path(args.repo_path).resolve(),
        enable_git_deploy=bool(args.enable_git_deploy),
        allow_push=bool(args.allow_push),
    )

    cascade_id = await orchestrator.trigger(args.trigger, context=context)
    print(f"Cascade started: {cascade_id}")

    previous = ""
    while True:
        status = await orchestrator.get_status(cascade_id)
        if status != previous:
            print(f"Status: {status}")
            previous = status
        if status in {"success", "failed", "not_found"}:
            break
        await asyncio.sleep(0.4)

    result = await orchestrator.get_result(cascade_id)
    if not result:
        print("No result produced.")
        return 2

    cascade: CascadeContext = result["cascade"]
    print("=" * 70)
    print(f"Result: {result['status']}")
    print(f"Cascade ID: {cascade.id}")
    print(f"Trigger: {cascade.trigger}")
    print(f"Agents activated: {len(cascade.agents_activated)}")
    print(f"Duration: {cascade.metrics.get('duration_seconds', 0.0):.2f}s")
    print(f"Quality: {cascade.outputs.get('final_validation', {}).get('quality_score', 0.0):.2f}")
    print(f"Deployments: {len(cascade.deployed_features)}")
    if cascade.errors:
        print(f"Errors: {len(cascade.errors)}")
    print("=" * 70)

    return 0 if result["status"] == "success" else 3


def main() -> int:
    return asyncio.run(run_cli_async())


if __name__ == "__main__":
    raise SystemExit(main())
