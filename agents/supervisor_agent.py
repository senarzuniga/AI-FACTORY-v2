"""
SUPERVISOR AGENT - El jefe de todo el sistema.
Interpreta intencion, decide workflow, asigna agentes, controla calidad.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class Intent(Enum):
    ANALYZE = "analyze"
    GENERATE_PROPOSAL = "generate_proposal"
    GENERATE_REPORT = "generate_report"
    GENERATE_PRESENTATION = "generate_presentation"
    VALIDATE = "validate"
    DELIVER = "deliver"
    COMPLEX = "complex"


@dataclass
class WorkflowDecision:
    intent: Intent
    required_agents: List[str]
    estimated_steps: int
    requires_human_approval: bool
    fallback_strategy: str


class SupervisorAgent:
    """
    El supervisor decide QUE hacer y COMO hacerlo.
    NO ejecuta - solo coordina.
    """

    def __init__(self) -> None:
        self.intent_history: List[Dict] = []

    def detect_intent(self, prompt: str, context: Dict) -> Intent:  # noqa: ARG002
        p = prompt.lower()
        if any(w in p for w in ("analiza", "analizar", "analisis", "insights")):
            return Intent.ANALYZE
        if any(w in p for w in ("propuesta", "proposal", "oferta")):
            return Intent.GENERATE_PROPOSAL
        if any(w in p for w in ("informe", "reporte", "report")):
            return Intent.GENERATE_REPORT
        if any(w in p for w in ("presentacion", "presentation", "ppt")):
            return Intent.GENERATE_PRESENTATION
        if any(w in p for w in ("valida", "validar", "revisar")):
            return Intent.VALIDATE
        if any(w in p for w in ("entrega", "deliver", "publica")):
            return Intent.DELIVER
        return Intent.COMPLEX

    def decide_workflow(self, intent: Intent, context: Dict) -> WorkflowDecision:  # noqa: ARG002
        _W = {
            Intent.ANALYZE: WorkflowDecision(
                intent=Intent.ANALYZE,
                required_agents=["data", "analysis", "validation", "memory"],
                estimated_steps=4,
                requires_human_approval=False,
                fallback_strategy="retry_with_more_context",
            ),
            Intent.GENERATE_PROPOSAL: WorkflowDecision(
                intent=Intent.GENERATE_PROPOSAL,
                required_agents=["data", "analysis", "generator", "generator2", "judge", "validation", "delivery"],
                estimated_steps=7,
                requires_human_approval=True,
                fallback_strategy="escalate_to_admin",
            ),
            Intent.GENERATE_REPORT: WorkflowDecision(
                intent=Intent.GENERATE_REPORT,
                required_agents=["data", "analysis", "generator", "validation", "delivery"],
                estimated_steps=5,
                requires_human_approval=False,
                fallback_strategy="regenerate",
            ),
            Intent.GENERATE_PRESENTATION: WorkflowDecision(
                intent=Intent.GENERATE_PRESENTATION,
                required_agents=["analysis", "generator", "validator", "delivery"],
                estimated_steps=4,
                requires_human_approval=False,
                fallback_strategy="use_template",
            ),
            Intent.VALIDATE: WorkflowDecision(
                intent=Intent.VALIDATE,
                required_agents=["validator"],
                estimated_steps=1,
                requires_human_approval=False,
                fallback_strategy="notify_human",
            ),
            Intent.DELIVER: WorkflowDecision(
                intent=Intent.DELIVER,
                required_agents=["delivery"],
                estimated_steps=1,
                requires_human_approval=True,
                fallback_strategy="save_to_drafts",
            ),
            Intent.COMPLEX: WorkflowDecision(
                intent=Intent.COMPLEX,
                required_agents=["data", "analysis", "generator", "validator", "memory", "delivery"],
                estimated_steps=6,
                requires_human_approval=True,
                fallback_strategy="human_intervention",
            ),
        }
        return _W.get(intent, _W[Intent.COMPLEX])

    def control_quality(self, output: Dict, expected_quality: str = "high") -> Dict:
        checks = {
            "completeness": self._check_completeness(output),
            "coherence": self._check_coherence(output),
            "data_consistency": self._check_data_consistency(output),
            "format_compliance": self._check_format(output),
        }
        passed = all(checks.values())
        return {
            "passed": passed,
            "checks": checks,
            "requires_human_review": not passed and expected_quality == "high",
        }

    def _check_completeness(self, output: Dict) -> bool:
        return all(f in output for f in ("content", "metadata", "sources"))

    def _check_coherence(self, output: Dict) -> bool:
        return len(output.get("content", "")) > 100

    def _check_data_consistency(self, output: Dict) -> bool:  # noqa: ARG002
        return True

    def _check_format(self, output: Dict) -> bool:
        return "content" in output
