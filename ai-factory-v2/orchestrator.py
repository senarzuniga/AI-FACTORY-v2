"""
AI Factory v2 — Orchestrator (CORE SYSTEM)

Entry point that coordinates all agents and controls the full cycle:

  INPUT → ANALYSIS → HYPOTHESES → SCORING → SELECTION → VALIDATION → EXECUTION → LEARNING

Run from the repository root (or inside ai-factory-v2/):

    python ai-factory-v2/orchestrator.py

Required environment variables:
  GITHUB_TOKEN       — Personal Access Token with repo write access
  GITHUB_REPOSITORY  — "owner/repo"
  OPENAI_API_KEY     — OpenAI API key
"""
from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Make the package importable when executed directly from its directory
sys.path.insert(0, str(Path(__file__).parent))

from openai import OpenAI

import config
from agents.analyzer import AnalyzerAgent
from agents.critic import CriticAgent
from agents.evaluator import EvaluatorAgent
from agents.executor import ExecutorAgent
from agents.generator import GeneratorAgent
from learning.registry import LearningRegistry
from models.hypothesis import CycleResult, Hypothesis, HypothesisStatus, Problem
from utils.github_client import GitHubClient
from utils.logger import get_logger, log_section

logger = get_logger("orchestrator")


class Orchestrator:
    """
    Coordinates the full AI Factory cycle.

    Architecture layers:
      2.1  Orchestrator   ← this class
      2.2  AnalyzerAgent
      2.3  GeneratorAgent
      2.4  EvaluatorAgent
      2.5  CriticAgent
      2.6  ExecutorAgent
    """

    def __init__(self) -> None:
        self._validate_config()

        self.github = GitHubClient(config.GITHUB_TOKEN, config.GITHUB_REPOSITORY)
        self.ai = OpenAI(api_key=config.OPENAI_API_KEY)

        self.analyzer = AnalyzerAgent(github_client=self.github, openai_client=self.ai)
        self.generator = GeneratorAgent(openai_client=self.ai)
        self.evaluator = EvaluatorAgent(openai_client=self.ai)
        self.critic = CriticAgent(openai_client=self.ai)
        self.executor = ExecutorAgent(github_client=self.github, openai_client=self.ai)
        self.learning = LearningRegistry(config.LEARNING_FILE)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self) -> CycleResult:
        """Execute one full AI Factory cycle and return the result."""
        cycle_id = f"cycle-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        result = CycleResult(cycle_id=cycle_id, repository=config.GITHUB_REPOSITORY)

        log_section(logger, f"AI FACTORY v2 — CYCLE {cycle_id}")

        # ── Step 1: Analyse repository ────────────────────────────────
        log_section(logger, "STEP 1 — Repository Analysis")
        problems = self._step_analyse(result)
        if not problems:
            return self._finish(result, rejected=True, reason="No improvement opportunities detected.")

        # ── Steps 2–9: Process each problem, stop after first PR ─────
        for problem in problems:
            log_section(logger, f"STEP 2-9 — Processing problem: {problem.title}")
            pr_created = self._process_problem(result, problem)
            if pr_created:
                break  # one PR per cycle (incremental changes)

        if not result.pr_url and not result.rejected:
            result.rejected = True
            result.rejection_reason = (
                "No hypothesis passed all validation gates for any detected problem."
            )

        # ── Step 9: Register learning ─────────────────────────────────
        log_section(logger, "STEP 9 — Register Learning")
        self._step_learn(result)

        log_section(logger, "CYCLE COMPLETE")
        self._log_cycle_summary(result)
        return result

    # ------------------------------------------------------------------
    # Individual steps
    # ------------------------------------------------------------------

    def _step_analyse(self, result: CycleResult) -> list[Problem]:
        problems = self.analyzer.analyse()
        result.problems = problems
        logger.info("Detected %d problem(s):", len(problems))
        for p in problems:
            logger.info("  [%s] %s (%s priority)", p.category, p.title, p.priority)
        return problems

    def _process_problem(self, result: CycleResult, problem: Problem) -> bool:
        """
        Run steps 3–8 for a single problem.
        Returns True if a PR was successfully created.
        """
        # Step 3: Generate hypotheses
        log_section(logger, "STEP 3 — Hypothesis Generation")
        hypotheses = self.generator.generate(problem, repo_context="")
        result.hypotheses.extend(hypotheses)

        if len(hypotheses) < config.MIN_HYPOTHESES:
            logger.warning(
                "Problem '%s' produced fewer than %d hypotheses — skipping.",
                problem.title,
                config.MIN_HYPOTHESES,
            )
            return False

        # Step 4: Evaluate and score
        log_section(logger, "STEP 4 — Evaluation & Scoring")
        hypotheses = self.evaluator.evaluate(problem, hypotheses)

        # Step 5: Select best
        log_section(logger, "STEP 5 — Selection")
        selected = self._pick_selected(hypotheses)
        if not selected:
            logger.warning(
                "No hypothesis met the scoring thresholds for '%s'.", problem.title
            )
            return False

        result.selected_hypothesis = selected
        logger.info("Selected: '%s' (composite=%.2f)", selected.title, selected.score.composite)  # type: ignore[union-attr]

        # Step 6: Critical validation
        log_section(logger, "STEP 6 — Critical Validation")
        selected = self.critic.validate(problem, selected)

        if selected.status != HypothesisStatus.APPROVED:
            result.rejected = True
            result.rejection_reason = (
                f"Critic blocked hypothesis '{selected.title}': {selected.critic_feedback}"
            )
            logger.warning("Execution BLOCKED by Critic Agent.")
            return False

        # Step 7–8: Execute and create PR
        log_section(logger, "STEP 7-8 — Execution & PR Creation")
        result = self.executor.execute(result, selected, problem, hypotheses)

        if result.pr_url:
            logger.info("PR created: %s", result.pr_url)
            return True

        return False

    def _step_learn(self, result: CycleResult) -> None:
        entry = self.learning.record(result)
        logger.info("Learning entry recorded — history size: %s", entry.get("cycle_id"))
        stats = self.learning.summary()
        logger.info(
            "Learning stats — total: %d | executed: %d | rejected: %d | success rate: %.0f%%",
            stats["total_cycles"],
            stats["executed"],
            stats["rejected"],
            stats["success_rate"] * 100,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pick_selected(hypotheses: list[Hypothesis]) -> Optional[Hypothesis]:
        return next(
            (h for h in hypotheses if h.status == HypothesisStatus.SELECTED), None
        )

    def _log_cycle_summary(self, result: CycleResult) -> None:
        logger.info("Cycle ID:            %s", result.cycle_id)
        logger.info("Repository:          %s", result.repository)
        logger.info("Problems detected:   %d", len(result.problems))
        logger.info("Hypotheses generated: %d", len(result.hypotheses))
        if result.selected_hypothesis:
            logger.info("Selected hypothesis: %s", result.selected_hypothesis.title)
        if result.pr_url:
            logger.info("PR created:          %s", result.pr_url)
        elif result.rejected:
            logger.info("Result:              REJECTED — %s", result.rejection_reason)

    @staticmethod
    def _validate_config() -> None:
        missing = []
        if not config.GITHUB_TOKEN:
            missing.append("GITHUB_TOKEN")
        if not config.GITHUB_REPOSITORY:
            missing.append("GITHUB_REPOSITORY")
        if not config.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    try:
        orchestrator = Orchestrator()
        result = orchestrator.run()
        return 0 if not result.rejected else 1
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        return 2
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during cycle: %s", exc)
        return 3


if __name__ == "__main__":
    sys.exit(main())
