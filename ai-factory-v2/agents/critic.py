"""
AI Factory v2 — Critic Agent

Provides final safety validation before any code change is executed.
Blocks execution if significant risks or uncertainties are detected.
"""
from __future__ import annotations

import json
from typing import Optional

from openai import OpenAI

import config
from models.hypothesis import Hypothesis, HypothesisStatus, Problem
from utils.logger import get_logger

logger = get_logger(__name__)

# Verdict values returned by the LLM
_VERDICT_APPROVE = "APPROVE"
_VERDICT_BLOCK = "BLOCK"


class CriticAgent:
    """
    Critically examines the selected hypothesis and approves or blocks it.

    Rule: if there is uncertainty → DO NOT execute.
    """

    SYSTEM_PROMPT = """\
You are the Critic Agent of AI Factory v2.

Your job is to detect flaws in the proposed solution, evaluate production risks,
and decide whether execution is safe.

Fundamental rule: "If there is uncertainty → DO NOT execute."

Examine the hypothesis critically and return a JSON object:
{
  "verdict":  "APPROVE" | "BLOCK",
  "risks":    ["<risk description>", ...],
  "feedback": "<detailed explanation of your decision>"
}

APPROVE only if ALL of the following hold:
- The implementation plan is concrete and unambiguous.
- The risk of breaking production is low.
- The change is incremental (not a full rewrite).
- The affected files are clearly identified.
- The plan includes validation or tests and a rollback path.

BLOCK if ANY of the following hold:
- The plan is vague or incomplete.
- The change could break production behaviour.
- Insufficient context is available.
- The change is too large or destructive.

Return ONLY a valid JSON object. No extra text.
"""

    def __init__(self, openai_client: Optional[OpenAI] = None) -> None:
        self.ai = openai_client or OpenAI(api_key=config.OPENAI_API_KEY)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, problem: Problem, hypothesis: Hypothesis) -> Hypothesis:
        """
        Validate the hypothesis and update its status to APPROVED or REJECTED.
        Returns the (mutated) hypothesis.
        """
        logger.info(
            "CriticAgent — validating hypothesis '%s' …", hypothesis.title
        )
        raw = self._call_llm(problem, hypothesis)
        verdict, risks, feedback = self._parse(raw)

        hypothesis.critic_feedback = feedback
        hypothesis.critic_risks = risks
        if verdict == _VERDICT_APPROVE:
            hypothesis.status = HypothesisStatus.APPROVED
            logger.info(
                "CriticAgent — APPROVED '%s'. Risks noted: %s",
                hypothesis.title,
                risks or "none",
            )
        else:
            hypothesis.status = HypothesisStatus.REJECTED
            logger.warning(
                "CriticAgent — BLOCKED '%s'. Reason: %s",
                hypothesis.title,
                feedback,
            )
        return hypothesis

    # ------------------------------------------------------------------
    # LLM interaction
    # ------------------------------------------------------------------

    def _call_llm(self, problem: Problem, hypothesis: Hypothesis) -> str:
        score_summary = hypothesis.score.to_dict() if hypothesis.score else {}
        user_message = (
            f"Problem: {problem.title}\n"
            f"Description: {problem.description}\n\n"
            f"Selected hypothesis:\n"
            f"  Title: {hypothesis.title}\n"
            f"  Approach: {hypothesis.approach}\n"
            f"  Description: {hypothesis.description}\n"
            f"  Implementation plan:\n{hypothesis.implementation_plan}\n"
            f"  Files to modify: {', '.join(hypothesis.files_to_modify) or 'not specified'}\n"
            f"  Evaluator rationale: {hypothesis.evaluation_rationale or 'none'}\n"
            f"  Score summary: {json.dumps(score_summary)}\n\n"
            "Provide your critical assessment."
        )
        response = self.ai.chat.completions.create(
            model=config.OPENAI_MODEL,
            temperature=0.1,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or "{}"

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse(self, raw: str) -> tuple[str, list[str], str]:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("CriticAgent — failed to parse LLM response: %s", exc)
            # Conservative default: block on parse error
            return _VERDICT_BLOCK, [], "Unable to parse critic response — blocking as precaution."

        verdict = data.get("verdict", _VERDICT_BLOCK).upper()
        if verdict not in (_VERDICT_APPROVE, _VERDICT_BLOCK):
            verdict = _VERDICT_BLOCK
        risks = data.get("risks", [])
        feedback = data.get("feedback", "No feedback provided.")
        return verdict, risks, feedback
