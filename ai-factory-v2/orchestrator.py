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

import json
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
from models.hypothesis import CycleResult, Hypothesis, HypothesisStatus, Problem, RepositoryAnalysis
from utils.github_client import GitHubClient
from utils.logger import get_logger, log_section

logger = get_logger("orchestrator")


class Orchestrator:
    """
    Coordinates the full AI Factory cycle for a single repository.

    Architecture layers:
      2.1  Orchestrator   <- this class
      2.2  AnalyzerAgent
      2.3  GeneratorAgent
      2.4  EvaluatorAgent
      2.5  CriticAgent
      2.6  ExecutorAgent
    """

    def __init__(self, repository: str) -> None:
        self.repository = repository
        self.github = GitHubClient(config.GITHUB_TOKEN, repository)
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
        result = CycleResult(cycle_id=cycle_id, repository=self.repository)

        log_section(logger, f"AI FACTORY v2 — CYCLE {cycle_id}")

        # ── Step 1: Analyse repository ────────────────────────────────
        log_section(logger, "STEP 1 — Repository Analysis")
        analysis = self._step_analyse(result)
        problems = analysis.problems
        if not problems:
            return self._finish(result, rejected=True, reason="No improvement opportunities detected.")

        # ── Steps 2–9: Process each problem, stop after first PR ─────
        for problem in problems:
            log_section(logger, f"STEP 2-9 — Processing problem: {problem.title}")
            pr_created = self._process_problem(result, problem, analysis)
            if pr_created:
                result.rejected = False
                result.rejection_reason = None
                break  # one PR per cycle (incremental changes)

        if not result.pr_url:
            result.rejected = True
            result.rejection_reason = result.rejection_reason or (
                "No hypothesis passed all validation gates for any detected problem."
            )

        # ── Step 9: Register learning ─────────────────────────────────
        log_section(logger, "STEP 9 — Register Learning")
        self._write_cycle_report(result)
        self._step_learn(result)

        log_section(logger, "CYCLE COMPLETE")
        self._log_cycle_summary(result)
        return result

    # ------------------------------------------------------------------
    # Individual steps
    # ------------------------------------------------------------------

    def _step_analyse(self, result: CycleResult) -> RepositoryAnalysis:
        analysis = self.analyzer.analyse()
        result.problems = analysis.problems
        result.analysis_summary = analysis.repository_summary
        result.analysis_notes = analysis.architecture_notes
        logger.info("Repository summary: %s", analysis.repository_summary)
        logger.info("Detected %d problem(s):", len(analysis.problems))
        for p in analysis.problems:
            logger.info("  [%s] %s (%s priority)", p.category, p.title, p.priority)
        return analysis

    def _process_problem(self, result: CycleResult, problem: Problem, analysis: RepositoryAnalysis) -> bool:
        """
        Run steps 3–8 for a single problem.
        Returns True if a PR was successfully created.
        """
        result.decision_log.append({
            "problem_id": problem.id,
            "problem_title": problem.title,
            "status": "under-review",
        })

        # Step 3: Generate hypotheses
        log_section(logger, "STEP 3 — Hypothesis Generation")
        hypotheses = self.generator.generate(problem, repo_context=analysis.repo_context)
        result.hypotheses.extend(hypotheses)

        if len(hypotheses) < config.MIN_HYPOTHESES:
            logger.warning(
                "Problem '%s' produced fewer than %d hypotheses — skipping.",
                problem.title,
                config.MIN_HYPOTHESES,
            )
            result.rejection_reason = (
                f"Problem '{problem.title}' did not yield enough structurally distinct hypotheses."
            )
            result.decision_log[-1]["status"] = "insufficient-hypotheses"
            return False

        # Step 4: Evaluate and score
        log_section(logger, "STEP 4 — Evaluation & Scoring")
        hypotheses = self.evaluator.evaluate(problem, hypotheses)

        # Step 5: Select best safe option(s)
        log_section(logger, "STEP 5 — Selection")
        candidates = self._rank_safe_hypotheses(hypotheses)
        if not candidates:
            logger.warning(
                "No hypothesis met the scoring thresholds for '%s'.", problem.title
            )
            result.rejection_reason = (
                f"No safe high-scoring hypothesis was found for '{problem.title}'."
            )
            result.decision_log[-1]["status"] = "no-safe-selection"
            return False

        result.decision_log[-1]["candidates_considered"] = [h.title for h in candidates]

        for index, selected in enumerate(candidates, start=1):
            result.selected_hypothesis = selected
            logger.info(
                "Selected candidate %d/%d: '%s' (composite=%.2f)",
                index,
                len(candidates),
                selected.title,
                selected.score.composite,
            )  # type: ignore[union-attr]

            # Step 6: Critical validation
            log_section(logger, "STEP 6 — Critical Validation")
            selected = self.critic.validate(problem, selected)

            if selected.status != HypothesisStatus.APPROVED:
                result.rejection_reason = (
                    f"Critic blocked hypothesis '{selected.title}': {selected.critic_feedback}"
                )
                result.decision_log[-1].setdefault("blocked_candidates", []).append(
                    {
                        "title": selected.title,
                        "reason": selected.critic_feedback,
                    }
                )
                logger.warning("Execution BLOCKED by Critic Agent for '%s'.", selected.title)
                continue

            # Step 7–8: Execute and create PR
            log_section(logger, "STEP 7-8 — Execution & PR Creation")
            if config.DRY_RUN:
                logger.info("DRY_RUN=true — skipping execution and PR creation.")
                result.rejected = True
                result.rejection_reason = "Execution skipped because DRY_RUN=true."
                result.decision_log[-1]["status"] = "dry-run"
                result.decision_log[-1]["selected_candidate"] = selected.title
                return False

            result = self.executor.execute(result, selected, problem, hypotheses)
            if result.pr_url:
                result.decision_log[-1]["status"] = "executed"
                result.decision_log[-1]["selected_candidate"] = selected.title
                result.decision_log[-1]["pr_url"] = result.pr_url
                logger.info("PR created: %s", result.pr_url)
                return True

            result.decision_log[-1].setdefault("blocked_candidates", []).append(
                {
                    "title": selected.title,
                    "reason": result.rejection_reason or "Execution safety gate blocked the change.",
                }
            )

        result.decision_log[-1]["status"] = "all-candidates-blocked"
        return False

    def _step_learn(self, result: CycleResult) -> None:
        refreshed = self.learning.refresh_pr_outcomes(self.github, self.repository)
        if refreshed:
            logger.info("Refreshed %d historical PR outcome(s).", refreshed)
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

    def _finish(self, result: CycleResult, *, rejected: bool, reason: str) -> CycleResult:
        """Mark result as rejected, register learning, and return the completed result."""
        result.rejected = rejected
        result.rejection_reason = reason
        log_section(logger, "STEP 9 — Register Learning")
        self._write_cycle_report(result)
        self._step_learn(result)
        log_section(logger, "CYCLE COMPLETE")
        self._log_cycle_summary(result)
        return result

    def _write_cycle_report(self, result: CycleResult) -> None:
        """Persist the full cycle report locally for auditability and learning."""
        output_dir = Path(config.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"{result.cycle_id}.json"
        result.report_path = str(report_path)
        report_path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _pick_selected(hypotheses: list[Hypothesis]) -> Optional[Hypothesis]:
        return next(
            (h for h in hypotheses if h.status == HypothesisStatus.SELECTED), None
        )

    @staticmethod
    def _rank_safe_hypotheses(hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        """Return all execution-eligible hypotheses ranked by composite score."""
        ranked = [
            h for h in hypotheses
            if h.score is not None and EvaluatorAgent._meets_execution_gate(h.score)
        ]
        return sorted(
            ranked,
            key=lambda h: h.score.composite if h.score else 0.0,
            reverse=True,
        )

    @staticmethod
    def _rank_safe_hypotheses(hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        """Return all execution-eligible hypotheses ranked by composite score."""
        ranked = [
            h for h in hypotheses
            if h.score is not None and EvaluatorAgent._meets_execution_gate(h.score)
        ]
        return sorted(
            ranked,
            key=lambda h: h.score.composite if h.score else 0.0,
            reverse=True,
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


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _validate_global_config() -> Optional[str]:
    """Return an error message if global required config is missing, else None."""
    missing = []
    if not config.GITHUB_TOKEN:
        missing.append("GITHUB_TOKEN")
    if not config.OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    return f"Missing required environment variables: {', '.join(missing)}" if missing else None


def _run_single_repo(repository: str) -> int:
    """Run one AI Factory cycle against a single repository. Returns exit code."""
    try:
        orchestrator = Orchestrator(repository)
        result = orchestrator.run()
        return 0 if not result.rejected else 1
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during cycle for '%s': %s", repository, exc)
        return 3


def _run_all_repos() -> int:
    """Discover every owned repository and run one cycle per repo."""
    log_section(logger, "MULTI-REPO MODE — Discovering repositories")
    try:
        all_repos = GitHubClient.discover_repos(
            config.GITHUB_TOKEN,
            skip_forks=config.SKIP_FORKS,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to discover repositories: %s", exc)
        return 2

    repos = [r for r in all_repos if r not in config.SKIP_REPOS]
    if not repos:
        logger.warning("No repositories to process (all discovered repos are in SKIP_REPOS).")
        return 1

    logger.info("Repositories to process (%d):", len(repos))
    for r in repos:
        logger.info("  - %s", r)

    results: dict[str, int] = {}
    for repo in repos:
        log_section(logger, f"CYCLE START: {repo}")
        results[repo] = _run_single_repo(repo)

    log_section(logger, "MULTI-REPO SUMMARY")
    pr_count = sum(1 for code in results.values() if code == 0)
    err_count = sum(1 for code in results.values() if code >= 2)
    logger.info("Repos processed : %d", len(results))
    logger.info("PRs created     : %d", pr_count)
    logger.info("Errors          : %d", err_count)
    for repo, code in results.items():
        status = "PR created" if code == 0 else ("rejected" if code == 1 else f"ERROR ({code})")
        logger.info("  %-40s %s", repo, status)

    return 0 if err_count == 0 else 3


def main() -> int:
    error = _validate_global_config()
    if error:
        logger.error("Configuration error: %s", error)
        return 2

    target = config.GITHUB_REPOSITORY.strip()
    if not target or target.upper() == "ALL":
        return _run_all_repos()
    return _run_single_repo(target)


if __name__ == "__main__":
    sys.exit(main())
