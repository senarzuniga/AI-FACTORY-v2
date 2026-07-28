"""Governance engine for engineering-policy decisions."""

from __future__ import annotations

from cognitive_os.models import GovernanceDecision


class Governance:
    """Policy checks that protect modularity, reuse, and interoperability."""

    def evaluate(
        self,
        *,
        touches_industrial_modules: bool,
        increases_modularity: bool,
        increases_reuse: bool,
        increases_interoperability: bool,
    ) -> GovernanceDecision:
        violations: list[str] = []
        if touches_industrial_modules:
            violations.append("industrial_business_module_change_not_allowed")
        if not increases_modularity:
            violations.append("no_modularity_improvement")
        if not increases_reuse:
            violations.append("no_reuse_improvement")
        if not increases_interoperability:
            violations.append("no_interoperability_improvement")

        if violations:
            return GovernanceDecision(
                approved=False,
                reason="Rejected by governance policy",
                policy_violations=violations,
            )

        return GovernanceDecision(approved=True, reason="Approved by governance policy")
