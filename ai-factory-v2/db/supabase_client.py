"""
AI Factory v2 — Supabase Data Store

Persists all cycle data (cycles, problems, hypotheses) to a Supabase
PostgreSQL database so that results from AI Factory v2 and any other
repositories sharing the same Supabase project are stored centrally.

The module is opt-in: if SUPABASE_URL or SUPABASE_KEY are not set the
store silently skips all writes rather than crashing the orchestrator.

Required environment variables (set as GitHub repository secrets):
    SUPABASE_URL   — e.g. https://<project-ref>.supabase.co
    SUPABASE_KEY   — service-role key (anon key works for select only)

Run the DDL in ai-factory-v2/db/schema.sql once via the Supabase SQL
editor before the first cycle so the tables exist.
"""
from __future__ import annotations

from typing import Optional

from models.hypothesis import CycleResult, Hypothesis, Problem
from utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseDataStore:
    """
    Thin wrapper around the Supabase Python client that persists AI Factory
    cycle results to three normalised tables:

        af_cycles        — one row per orchestration cycle
        af_problems      — one row per detected problem (FK → af_cycles)
        af_hypotheses    — one row per generated hypothesis (FK → af_cycles)
    """

    def __init__(self, url: str, key: str) -> None:
        from supabase import create_client  # deferred import — optional dep

        self._client = create_client(url, key)
        logger.info("SupabaseDataStore — connected to %s", url)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def persist_cycle(self, result: CycleResult) -> None:
        """
        Upsert a complete cycle result (cycle + problems + hypotheses) into
        Supabase.  Any individual table failure is caught and logged so that
        a Supabase write error never aborts the orchestrator.
        """
        try:
            self._upsert_cycle(result)
        except Exception as exc:  # noqa: BLE001
            logger.error("SupabaseDataStore — failed to persist cycle: %s", exc)
            return

        for problem in result.problems:
            try:
                self._upsert_problem(problem, result.cycle_id)
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "SupabaseDataStore — failed to persist problem '%s': %s",
                    problem.id,
                    exc,
                )

        for hypothesis in result.hypotheses:
            try:
                self._upsert_hypothesis(hypothesis, result.cycle_id)
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "SupabaseDataStore — failed to persist hypothesis '%s': %s",
                    hypothesis.id,
                    exc,
                )

        logger.info(
            "SupabaseDataStore — persisted cycle %s (%d problems, %d hypotheses)",
            result.cycle_id,
            len(result.problems),
            len(result.hypotheses),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _upsert_cycle(self, result: CycleResult) -> None:
        row: dict = {
            "cycle_id": result.cycle_id,
            "repository": result.repository,
            "problems_count": len(result.problems),
            "hypotheses_count": len(result.hypotheses),
            "rejected": result.rejected,
            "rejection_reason": result.rejection_reason,
            "pr_url": result.pr_url,
            "pr_number": result.pr_number,
        }
        if result.selected_hypothesis:
            h = result.selected_hypothesis
            row["selected_hypothesis_id"] = h.id
            row["selected_hypothesis_title"] = h.title
            if h.score:
                row["selected_score_composite"] = round(h.score.composite, 2)

        self._client.table("af_cycles").upsert(row).execute()

    def _upsert_problem(self, problem: Problem, cycle_id: str) -> None:
        row: dict = {
            "id": problem.id,
            "cycle_id": cycle_id,
            "title": problem.title,
            "description": problem.description,
            "category": problem.category,
            "priority": problem.priority,
            "affected_files": problem.affected_files,
        }
        self._client.table("af_problems").upsert(row).execute()

    def _upsert_hypothesis(self, hypothesis: Hypothesis, cycle_id: str) -> None:
        row: dict = {
            "id": hypothesis.id,
            "cycle_id": cycle_id,
            "problem_id": hypothesis.problem_id,
            "title": hypothesis.title,
            "description": hypothesis.description,
            "approach": hypothesis.approach,
            "implementation_plan": hypothesis.implementation_plan,
            "status": hypothesis.status.value,
            "critic_feedback": hypothesis.critic_feedback,
        }
        if hypothesis.score:
            s = hypothesis.score
            row["score_composite"] = round(s.composite, 2)
            row["score_business_impact"] = s.business_impact
            row["score_technical_risk"] = s.technical_risk
            row["score_complexity"] = s.complexity
            row["score_maintainability"] = s.maintainability
            row["score_scalability"] = s.scalability

        self._client.table("af_hypotheses").upsert(row).execute()


# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------

def create_supabase_store(url: str, key: str) -> Optional[SupabaseDataStore]:
    """
    Return a SupabaseDataStore if both credentials are provided, otherwise
    log a notice and return None so callers can skip Supabase writes safely.
    """
    if not url or not key:
        logger.info(
            "SupabaseDataStore — SUPABASE_URL/KEY not set; "
            "Supabase persistence is disabled."
        )
        return None
    try:
        return SupabaseDataStore(url, key)
    except Exception as exc:  # noqa: BLE001
        logger.error("SupabaseDataStore — could not initialise client: %s", exc)
        return None
