"""Grounding agent that converts plans into deterministic change specs."""

from __future__ import annotations

from dataclasses import dataclass
import difflib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class GroundingResult:
    code_changes: List[Dict[str, Any]]
    feedback: Dict[str, Any]


class GroundingAgent:
    def __init__(self, config: Dict[str, Any], repo_path: Path):
        self.config = config
        self.repo_path = repo_path
        self.grounding_success_rate = 0.0
        self.ambiguous_patterns: List[str] = []

    async def ground_plan(self, plan: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        changes: List[Dict[str, Any]] = []
        feedback: Dict[str, Any] = {"successful": True, "ambiguous_steps": [], "suggestions": []}

        for step in plan.get("steps", []):
            change = await self._ground_step(step)
            if change:
                changes.append(change)
            else:
                feedback["successful"] = False
                feedback["ambiguous_steps"].append(
                    {"step_id": step.get("step_id"), "reason": "Could not determine concrete implementation"}
                )
                feedback["suggestions"].append(
                    f"Step {step.get('step_id')} should include exact code targets and validation commands."
                )

        self._update_success_rate(feedback["successful"])
        return changes, feedback

    async def _ground_step(self, step: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        target_files = [p for p in step.get("target_files", []) if (self.repo_path / p).exists()]
        if not target_files:
            return None

        change_specs: List[Dict[str, Any]] = []
        for file_path in target_files:
            content = (self.repo_path / file_path).read_text(encoding="utf-8", errors="ignore")
            if "TODO" in content:
                change_specs.append(
                    {
                        "type": "replace",
                        "search_pattern": "TODO",
                        "new_code": "DONE",
                    }
                )

        if not change_specs:
            return {
                "file": target_files[0],
                "changes": [],
                "validation": "No-op grounding; requires human/LLM refinement.",
            }

        return {"file": target_files[0], "changes": change_specs, "validation": "Run targeted tests and lint"}

    async def apply_changes(self, changes: List[Dict[str, Any]], dry_run: bool = True) -> Dict[str, Any]:
        results: Dict[str, Any] = {"applied": [], "failed": [], "validation": {}}
        for change in changes:
            file_rel = change.get("file")
            if not file_rel:
                continue
            file_path = self.repo_path / file_rel
            if not file_path.exists():
                results["failed"].append({"file": file_rel, "reason": "File does not exist"})
                continue

            original = file_path.read_text(encoding="utf-8", errors="ignore")
            modified = original
            for spec in change.get("changes", []):
                modified = self._apply_by_pattern(modified, spec)

            if not dry_run and modified != original:
                file_path.write_text(modified, encoding="utf-8")

            diff = self._generate_diff(original, modified)
            results["applied"].append({"file": file_rel, "diff": diff, "validation": change.get("validation")})

        if not dry_run:
            results["validation"] = await self._validate_changes(results["applied"])
        return results

    def _apply_by_pattern(self, content: str, change_spec: Dict[str, Any]) -> str:
        pattern = change_spec.get("search_pattern", "")
        replacement = change_spec.get("new_code", "")
        if not pattern:
            return content
        if change_spec.get("type") == "replace":
            return content.replace(pattern, replacement)
        if change_spec.get("type") == "regex_replace":
            return re.sub(pattern, replacement, content)
        return content

    def _generate_diff(self, original: str, modified: str) -> str:
        diff = difflib.unified_diff(
            original.splitlines(),
            modified.splitlines(),
            fromfile="original",
            tofile="modified",
            lineterm="",
        )
        return "\n".join(diff)

    def _update_success_rate(self, success: bool) -> None:
        self.grounding_success_rate = self.grounding_success_rate * 0.9 + (0.1 if success else 0.0)

    async def _validate_changes(self, applied_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        validation: Dict[str, Any] = {"syntax_ok": True, "issues": []}
        for change in applied_changes:
            file_name = change.get("file", "")
            if file_name.endswith(".py"):
                proc = subprocess.run(
                    ["python", "-m", "py_compile", str(self.repo_path / file_name)],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    validation["syntax_ok"] = False
                    validation["issues"].append({"file": file_name, "error": proc.stderr})
        return validation

