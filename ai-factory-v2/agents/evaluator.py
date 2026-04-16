"""
AI Factory v2 — Evaluator Agent

Scores every hypothesis across five criteria and selects the best candidate.
"""
from __future__ import annotations

import json
from typing import Optional

from openai import OpenAI

import config
from models.hypothesis import Hypothesis, HypothesisScore, HypothesisStatus, Problem
from utils.logger import get_logger, log_dict

logger = get_logger(__name__)


class EvaluatorAgent:
    """
    Compares all hypotheses for a problem and assigns numeric scores.

    Scoring criteria (0–10 each):
    - business_impact    (higher is better)
    - technical_risk     (lower is better)
    - complexity         (lower is better)
    - maintainability    (higher is better)
    - scalability        (higher is better)

    The composite score is computed by HypothesisScore.composite.
    Only hypotheses meeting the thresholds defined in config can be selected.
    """

    SYSTEM_PROMPT = """\
You are the Evaluator Agent of AI Factory v2.

Your job is to score a list of hypotheses for a given problem using five criteria.

Scoring criteria (0–10 each):
- business_impact:   real value this solution delivers (10 = maximum value)
- technical_risk:    probability of failure or breaking things (0 = safest)
- complexity:        difficulty of implementation (0 = simplest)
- maintainability:   how easy the code will be to maintain afterwards (10 = easiest)
- scalability:       how well the solution will scale (10 = best)

Return a JSON array with one object per hypothesis, in the SAME ORDER as the input list:
[
  {
    "hypothesis_id":   "<id from input>",
    "business_impact": <0-10>,
    "technical_risk":  <0-10>,
    "complexity":      <0-10>,
    "maintainability": <0-10>,
    "scalability":     <0-10>,
    "rationale":       "<brief justification>"
  },
  ...
]

Return ONLY a valid JSON array. No extra text.
"""

    def __init__(self, openai_client: Optional[OpenAI] = None) -> None:
        self.ai = openai_client or OpenAI(api_key=config.OPENAI_API_KEY)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, problem: Problem, hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        """Score all hypotheses and mark the winner as SELECTED (if it passes thresholds)."""
        if not hypotheses:
            return []

        logger.info(
            "EvaluatorAgent — scoring %d hypothesis/hypotheses for '%s' …",
            len(hypotheses),
            problem.title,
        )

        raw = self._call_llm(problem, hypotheses)
        scores = self._parse_scores(raw, hypotheses)
        self._apply_scores(hypotheses, scores)
        self._log_scoreboard(hypotheses)
        self._select_best(hypotheses)
        return hypotheses

    # ------------------------------------------------------------------
    # LLM interaction
    # ------------------------------------------------------------------

    def _call_llm(self, problem: Problem, hypotheses: list[Hypothesis]) -> str:
        hyp_list = "\n".join(
            f'{i+1}. ID={h.id} | Title="{h.title}" | Approach="{h.approach}"\n'
            f"   Description: {h.description[:500]}"
            for i, h in enumerate(hypotheses)
        )
        user_message = (
            f"Problem: {problem.title}\n"
            f"Description: {problem.description}\n\n"
            f"Hypotheses to score:\n{hyp_list}\n\n"
            "Score each hypothesis and return the JSON array."
        )
        response = self.ai.chat.completions.create(
            model=config.OPENAI_MODEL,
            temperature=0.1,  # deterministic scoring
            max_tokens=config.OPENAI_MAX_TOKENS,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or "[]"

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse_scores(
        self, raw: str, hypotheses: list[Hypothesis]
    ) -> dict[str, tuple[HypothesisScore, str]]:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            items = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("EvaluatorAgent — failed to parse LLM response: %s", exc)
            return {}

        result: dict[str, tuple[HypothesisScore, str]] = {}
        for item in items:
            h_id = item.get("hypothesis_id", "")
            if not h_id:
                idx = items.index(item)
                if idx < len(hypotheses):
                    h_id = hypotheses[idx].id
            if not h_id:
                continue
            try:
                score = HypothesisScore(
                    business_impact=float(item.get("business_impact", 0)),
                    technical_risk=float(item.get("technical_risk", 10)),
                    complexity=float(item.get("complexity", 10)),
                    maintainability=float(item.get("maintainability", 0)),
                    scalability=float(item.get("scalability", 0)),
                )
                result[h_id] = (score, item.get("rationale", ""))
            except (TypeError, ValueError) as exc:
                logger.warning("EvaluatorAgent — bad score entry for %s: %s", h_id, exc)
        return result

    # ------------------------------------------------------------------
    # Score application
    # ------------------------------------------------------------------

    def _apply_scores(
        self, hypotheses: list[Hypothesis], scores: dict[str, tuple[HypothesisScore, str]]
    ) -> None:
        for h in hypotheses:
            if h.id in scores:
                score, rationale = scores[h.id]
                h.score = score
                h.evaluation_rationale = rationale
                h.status = HypothesisStatus.EVALUATED
            else:
                logger.warning("EvaluatorAgent — no score found for hypothesis '%s'", h.id)

    def _select_best(self, hypotheses: list[Hypothesis]) -> None:
        evaluated = [h for h in hypotheses if h.score is not None]
        if not evaluated:
            return

        evaluated.sort(key=lambda h: h.score.composite, reverse=True)  # type: ignore[union-attr]
        for hypothesis in evaluated:
            hypothesis.status = HypothesisStatus.REJECTED

        eligible = [h for h in evaluated if self._meets_execution_gate(h.score)]
        if eligible:
            best = eligible[0]
            best.status = HypothesisStatus.SELECTED
            logger.info(
                "EvaluatorAgent — SELECTED '%s' (composite=%.2f)",
                best.title,
                best.score.composite,  # type: ignore[union-attr]
            )
            return

        best = evaluated[0]
        logger.warning(
            "EvaluatorAgent — best hypothesis '%s' failed execution gates "
            "(impact=%.1f, risk=%.1f, complexity=%.1f, maintainability=%.1f, scalability=%.1f, composite=%.2f).",
            best.title,
            best.score.business_impact,  # type: ignore[union-attr]
            best.score.technical_risk,  # type: ignore[union-attr]
            best.score.complexity,  # type: ignore[union-attr]
            best.score.maintainability,  # type: ignore[union-attr]
            best.score.scalability,  # type: ignore[union-attr]
            best.score.composite,  # type: ignore[union-attr]
        )

    @staticmethod
    def _meets_execution_gate(score: Optional[HypothesisScore]) -> bool:
        if score is None:
            return False
        return (
            score.business_impact >= config.MIN_BUSINESS_IMPACT
            and score.technical_risk <= config.MAX_TECHNICAL_RISK
            and score.maintainability >= config.MIN_MAINTAINABILITY
            and score.scalability >= config.MIN_SCALABILITY
            and score.complexity <= config.MAX_COMPLEXITY
            and score.composite >= config.MIN_COMPOSITE_SCORE
        )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log_scoreboard(self, hypotheses: list[Hypothesis]) -> None:
        logger.info("EvaluatorAgent — scoreboard:")
        for h in hypotheses:
            if h.score:
                log_dict(
                    logger,
                    f"  {h.title[:50]}",
                    {
                        "business_impact": h.score.business_impact,
                        "technical_risk": h.score.technical_risk,
                        "complexity": h.score.complexity,
                        "maintainability": h.score.maintainability,
                        "scalability": h.score.scalability,
                        "COMPOSITE": f"{h.score.composite:.2f}",
                    },
                )
