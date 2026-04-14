"""
AI Factory v2 — Hypothesis Generator Agent

Generates 2–5 structurally different hypotheses for each detected problem.
"""
from __future__ import annotations

import json
import uuid
from typing import Optional

from openai import OpenAI

import config
from models.hypothesis import Hypothesis, Problem
from utils.logger import get_logger

logger = get_logger(__name__)


class GeneratorAgent:
    """
    For each Problem, generates MIN_HYPOTHESES–MAX_HYPOTHESES candidate solutions.

    Each hypothesis must differ structurally from the others (no minor variants).
    """

    SYSTEM_PROMPT = """\
You are the Hypothesis Generator Agent of AI Factory v2.

Your job is to generate multiple candidate solutions (hypotheses) for a given problem.

Rules:
- Generate between {min_h} and {max_h} hypotheses.
- Each hypothesis MUST differ STRUCTURALLY from the others (different approach, not just different wording).
- Do NOT generate minor variations of the same idea (e.g., rename variable → rename method).
- Valid approaches: architecture refactor, algorithm optimisation, logic simplification,
  design pattern adoption, dependency replacement, caching strategy, etc.

Return a JSON array where each element has:
{{
  "title":               "<short title>",
  "description":         "<detailed description of what this solution does>",
  "approach":            "<one-line structural approach label>",
  "implementation_plan": "<numbered step-by-step plan to implement>",
  "files_to_modify":     ["<path>", ...]
}}

Return ONLY a valid JSON array. No extra text.
"""

    def __init__(self, openai_client: Optional[OpenAI] = None) -> None:
        self.ai = openai_client or OpenAI(api_key=config.OPENAI_API_KEY)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, problem: Problem, repo_context: str = "") -> list[Hypothesis]:
        """Generate hypotheses for a single Problem."""
        logger.info(
            "GeneratorAgent — generating hypotheses for problem '%s' …", problem.title
        )
        raw = self._call_llm(problem, repo_context)
        hypotheses = self._parse(raw, problem)

        if len(hypotheses) < config.MIN_HYPOTHESES:
            logger.error(
                "GeneratorAgent — only %d hypothesis/hypotheses returned for '%s'; "
                "minimum is %d. Skipping problem.",
                len(hypotheses),
                problem.title,
                config.MIN_HYPOTHESES,
            )
            return []

        # Cap at MAX_HYPOTHESES
        hypotheses = hypotheses[: config.MAX_HYPOTHESES]
        logger.info(
            "GeneratorAgent — %d hypothesis/hypotheses generated for '%s'",
            len(hypotheses),
            problem.title,
        )
        return hypotheses

    # ------------------------------------------------------------------
    # LLM interaction
    # ------------------------------------------------------------------

    def _call_llm(self, problem: Problem, repo_context: str) -> str:
        system = self.SYSTEM_PROMPT.format(
            min_h=config.MIN_HYPOTHESES,
            max_h=config.MAX_HYPOTHESES,
        )
        user_parts = [
            f"Problem ID: {problem.id}",
            f"Title: {problem.title}",
            f"Description: {problem.description}",
            f"Category: {problem.category}",
            f"Affected files: {', '.join(problem.affected_files) or 'unknown'}",
            f"Priority: {problem.priority}",
        ]
        if repo_context:
            user_parts.append(f"\nRepository context:\n{repo_context[:10_000]}")
        user_parts.append("\nGenerate the hypotheses JSON array.")

        response = self.ai.chat.completions.create(
            model=config.OPENAI_MODEL,
            temperature=config.OPENAI_TEMPERATURE + 0.1,  # slightly more creative
            max_tokens=config.OPENAI_MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
        )
        return response.choices[0].message.content or "[]"

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse(self, raw: str, problem: Problem) -> list[Hypothesis]:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            items = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("GeneratorAgent — failed to parse LLM response: %s", exc)
            return []

        hypotheses: list[Hypothesis] = []
        for item in items:
            h_id = f"{problem.id}-h{len(hypotheses)+1:02d}-{uuid.uuid4().hex[:6]}"
            try:
                hypotheses.append(
                    Hypothesis(
                        id=h_id,
                        problem_id=problem.id,
                        title=item.get("title", f"Hypothesis {len(hypotheses)+1}"),
                        description=item.get("description", ""),
                        approach=item.get("approach", "general"),
                        implementation_plan=item.get("implementation_plan", ""),
                        files_to_modify=item.get("files_to_modify", []),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("GeneratorAgent — skipping malformed hypothesis: %s", exc)
        return hypotheses
