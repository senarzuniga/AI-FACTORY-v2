"""
AI Factory v2 — Analysis Agent (Planner / Scout)

Reads the repository content and identifies improvement opportunities.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from openai import OpenAI

import config
from models.hypothesis import Problem, RepositoryAnalysis
from utils.github_client import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


class AnalyzerAgent:
    """
    Reads the repository and produces a list of Problems.

    The agent:
    1. Collects source files from the repository (via GitHub API or local FS).
    2. Sends a structured snapshot to the LLM.
    3. Parses the LLM's response into Problem objects.
    """

    SYSTEM_PROMPT = """\
You are the Analysis Agent (Planner/Scout) of AI Factory v2.

Your job is to:
1. Read a snapshot of the full repository.
2. Summarize the current architecture and quality posture.
3. Identify concrete improvement opportunities (problems).
4. Return a single JSON object.

Return this schema:
{
  "repository_summary": "<2-4 sentence summary>",
  "architecture_notes": ["<important architectural observation>", ...],
  "improvement_opportunities": ["<high-value opportunity>", ...],
  "problems": [
    {
      "id": "<short slug>",
      "title": "<brief title>",
      "description": "<detailed description>",
      "category": "<architecture|performance|security|maintainability|testing|documentation>",
      "affected_files": ["<path>", ...],
      "priority": "<low|medium|high|critical>"
    }
  ]
}

Rules:
- Return ONLY valid JSON. No markdown.
- Identify at most 5 problems per cycle.
- Each problem must be actionable and structurally meaningful.
- Do NOT suggest trivial renames or micro-adjustments.
- If no meaningful problems are found, return an empty problems array.
"""

    def __init__(
        self,
        github_client: Optional[GitHubClient] = None,
        openai_client: Optional[OpenAI] = None,
    ) -> None:
        self.github = github_client
        self.ai = openai_client or OpenAI(api_key=config.OPENAI_API_KEY)
        self.local_root = config.APP_DIR.parent
        self.last_analysis = RepositoryAnalysis()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyse(self) -> RepositoryAnalysis:
        """Analyse the repository and return structured repository context."""
        logger.info("AnalyzerAgent — collecting repository snapshot …")
        snapshot = self._build_snapshot()
        logger.info("AnalyzerAgent — snapshot size: %d chars", len(snapshot))
        raw = self._call_llm(snapshot)
        analysis = self._parse_analysis(raw, snapshot)
        self.last_analysis = analysis
        logger.info("AnalyzerAgent — detected %d problem(s)", len(analysis.problems))
        return analysis

    # ------------------------------------------------------------------
    # Snapshot building
    # ------------------------------------------------------------------

    def _build_snapshot(self) -> str:
        """Return a textual snapshot of the repository contents."""
        if self.github:
            return self._snapshot_from_github()
        return self._snapshot_from_filesystem()

    def _snapshot_from_github(self) -> str:
        assert self.github is not None
        files = self.github.list_repo_files()
        return self._collect_files(files, source="github")

    def _snapshot_from_filesystem(self) -> str:
        root = self.local_root
        files: list[str] = []
        for p in root.rglob("*"):
            if p.is_file():
                parts = p.parts
                if any(skip in parts for skip in config.SKIP_DIRS):
                    continue
                if p.suffix in config.ANALYSED_EXTENSIONS:
                    files.append(p.relative_to(root).as_posix())
        return self._collect_files(files, source="filesystem")

    def _collect_files(self, file_paths: list[str], source: str) -> str:
        chunks: list[str] = []
        total = 0
        for path in sorted(file_paths):
            ext = Path(path).suffix
            if ext not in config.ANALYSED_EXTENSIONS:
                continue
            content = self._read_file(path, source)
            if not content:
                continue
            content = content[: config.MAX_FILE_CHARS]
            chunk = f"### FILE: {path}\n```\n{content}\n```\n"
            total += len(chunk)
            if total > config.MAX_REPO_CHARS:
                logger.info("AnalyzerAgent — snapshot limit reached, stopping at '%s'", path)
                break
            chunks.append(chunk)
        return "\n".join(chunks)

    def _read_file(self, path: str, source: str) -> Optional[str]:
        if source == "github" and self.github:
            return self.github.get_file_content(path)
        try:
            return (self.local_root / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    # ------------------------------------------------------------------
    # LLM interaction
    # ------------------------------------------------------------------

    def _call_llm(self, snapshot: str) -> str:
        user_message = (
            f"Repository snapshot:\n\n{snapshot}\n\n"
            "Identify improvement opportunities and return the structured JSON object."
        )
        response = self.ai.chat.completions.create(
            model=config.OPENAI_MODEL,
            temperature=config.OPENAI_TEMPERATURE,
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

    def _parse_analysis(self, raw: str, snapshot: str) -> RepositoryAnalysis:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("AnalyzerAgent — failed to parse LLM response: %s", exc)
            logger.debug("Raw response: %s", raw)
            return RepositoryAnalysis(
                repository_summary="Repository analysis could not be fully parsed.",
                architecture_notes=[],
                improvement_opportunities=[],
                repo_context=snapshot,
                problems=[],
            )

        if isinstance(data, list):
            payload = {
                "repository_summary": "Repository scanned and candidate improvements were identified.",
                "architecture_notes": [],
                "improvement_opportunities": [item.get("title", "Unnamed opportunity") for item in data[:5] if isinstance(item, dict)],
                "problems": data,
            }
        else:
            payload = data

        problems: list[Problem] = []
        for item in payload.get("problems", []):
            if not isinstance(item, dict):
                continue
            try:
                problems.append(
                    Problem(
                        id=item.get("id", f"prob-{len(problems)+1:03d}"),
                        title=item.get("title", "Unnamed problem"),
                        description=item.get("description", ""),
                        category=item.get("category", "general"),
                        affected_files=item.get("affected_files", []),
                        priority=item.get("priority", "medium"),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("AnalyzerAgent — skipping malformed problem entry: %s", exc)

        return RepositoryAnalysis(
            repository_summary=payload.get("repository_summary", "Repository scanned for improvements."),
            architecture_notes=payload.get("architecture_notes", []),
            improvement_opportunities=payload.get("improvement_opportunities", []),
            repo_context=snapshot,
            problems=problems,
        )
