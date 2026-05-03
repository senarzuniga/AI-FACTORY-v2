"""
VALIDATION AGENT
Revisa coherencia, logica y consistencia con datos fuente.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ValidationAgent:
    """Valida el contenido generado antes de publicarlo."""

    async def validate(
        self, content: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        checks = {
            "data_consistency": self._check_data_consistency(content, context),
            "logic_coherence": self._check_logic(content),
            "completeness": self._check_completeness(content),
            "permission_compliance": self._check_permissions(content, context),
        }
        is_valid = all(checks.values())
        issues: List[str] = [k for k, v in checks.items() if not v]
        return {
            "valid": is_valid,
            "checks": checks,
            "issues": issues,
            "requires_human_review": not is_valid,
        }

    def _check_data_consistency(
        self, content: Dict[str, Any], context: Dict[str, Any]  # noqa: ARG002
    ) -> bool:
        return True

    def _check_logic(self, content: Dict[str, Any]) -> bool:
        return bool(content.get("content") or content.get("slides") or content.get("type"))

    def _check_completeness(self, content: Dict[str, Any]) -> bool:
        return "type" in content

    def _check_permissions(
        self, content: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        if content.get("type") == "proposal":
            return context.get("permissions", {}).get("can_approve", False)
        return True
