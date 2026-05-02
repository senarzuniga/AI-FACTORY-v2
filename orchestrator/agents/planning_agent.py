"""Planning agent for generating actionable repository improvement plans."""

from __future__ import annotations

from datetime import datetime
import json
from typing import Any, Dict, List

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    AsyncOpenAI = None


class PlanningAgent:
    def __init__(self, config: Dict[str, Any], model: str = "gpt-4-turbo-preview"):
        self.config = config
        self.model = model
        self.openai_client = (
            AsyncOpenAI(api_key=config.get("openai_api_key"))
            if AsyncOpenAI and config.get("openai_api_key")
            else None
        )
        self.planning_history: List[Dict[str, Any]] = []
        self.grounding_feedback: List[Dict[str, Any]] = []

    async def generate_plan(self, repository_analysis: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        if self.openai_client is None:
            return self._fallback_plan(repository_analysis)

        prompt = self._build_planning_prompt(repository_analysis, constraints)
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=float(self.config.get("temperature", 0.7)),
            max_tokens=int(self.config.get("max_tokens", 4000)),
        )

        content = response.choices[0].message.content or "{}"
        plan = self._parse_plan(content)
        self.planning_history.append(
            {
                "analysis_hash": hash(json.dumps(repository_analysis, sort_keys=True, default=str)),
                "plan": plan,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return plan

    async def refine_plan(self, plan: Dict[str, Any], grounding_feedback: Dict[str, Any]) -> Dict[str, Any]:
        if self.openai_client is None:
            refined = dict(plan)
            refined.setdefault("steps", []).append(
                {
                    "step_id": len(refined.get("steps", [])) + 1,
                    "description": "Resolve ambiguous grounding points with explicit file targets and validation commands.",
                    "target_files": grounding_feedback.get("likely_files", []),
                    "expected_outcome": "Plan is directly executable with minimal ambiguity.",
                    "risk_level": "low",
                    "validation_criteria": ["No ambiguous step remains"],
                }
            )
            return refined

        prompt = (
            "Refine the plan to remove ambiguity and increase grounding precision.\n"
            f"Plan:\n{json.dumps(plan, indent=2)}\n"
            f"Feedback:\n{json.dumps(grounding_feedback, indent=2)}"
        )

        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Produce precise, low-risk, implementation-ready plans."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=4000,
        )

        refined_plan = self._parse_plan(response.choices[0].message.content or "{}")
        self.grounding_feedback.append(
            {
                "original_plan": plan,
                "feedback": grounding_feedback,
                "refined_plan": refined_plan,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return refined_plan

    def _get_system_prompt(self) -> str:
        return (
            "You are an expert planning agent for autonomous code improvement. "
            "Produce specific file-targeted steps with measurable validation and rollback criteria."
        )

    def _build_planning_prompt(self, analysis: Dict[str, Any], constraints: Dict[str, Any]) -> str:
        return (
            f"Repository structure: {json.dumps(analysis.get('structure', {}))}\n"
            f"Issues: {json.dumps(analysis.get('issues', []))}\n"
            f"Opportunities: {json.dumps(analysis.get('opportunities', []))}\n"
            f"Constraints: {json.dumps(constraints)}"
        )

    def _parse_plan(self, response: str) -> Dict[str, Any]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass
        return self._fallback_plan({})

    def _fallback_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        targets = analysis.get("candidate_files", [])[:3]
        return {
            "overview": "Fallback deterministic plan",
            "steps": [
                {
                    "step_id": 1,
                    "description": "Implement a minimal, test-backed fix for top-ranked issue.",
                    "target_files": targets,
                    "expected_outcome": "Issue reduced without regressions",
                    "risk_level": "low",
                    "validation_criteria": ["tests pass", "lint pass"],
                }
            ],
            "total_risk": "low",
            "estimated_impact": "incremental",
            "dependencies": [],
        }

