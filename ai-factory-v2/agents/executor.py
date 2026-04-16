"""
AI Factory v2 — Executor Agent (PR Engine)

Applies the approved hypothesis as a minimal code change on a new branch
and opens a Pull Request.
"""
from __future__ import annotations

import ast
import json
import re
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Optional

from openai import OpenAI

import config
from models.hypothesis import CycleResult, Hypothesis, HypothesisStatus, Problem
from utils.github_client import GitHubClient
from utils.logger import get_logger

logger = get_logger(__name__)


class ExecutorAgent:
    """
    Responsible for:
    1. Asking the LLM to generate the exact file content changes required.
    2. Creating a new branch.
    3. Committing the changes.
    4. Opening a Pull Request with a detailed description.

    Rule: NEVER commit directly to main.
    """

    CHANGE_SYSTEM_PROMPT = """\
You are the Executor Agent of AI Factory v2.

Your job is to produce the minimal, safe file changes needed to implement a hypothesis.

You will receive:
- A hypothesis (title, approach, implementation plan, files to modify).
- The current content of each relevant file (if available).

Return a JSON array of file changes:
[
  {
    "path":    "<relative file path>",
    "content": "<complete new file content as a string>"
  },
  ...
]

Rules:
- Return ONLY the files that need to change.
- Keep changes minimal and surgical.
- Preserve existing style, indentation, and conventions.
- Do NOT introduce breaking changes.
- Return ONLY a valid JSON array. No extra text.
"""

    def __init__(
        self,
        github_client: GitHubClient,
        openai_client: Optional[OpenAI] = None,
    ) -> None:
        self.github = github_client
        self.ai = openai_client or OpenAI(api_key=config.OPENAI_API_KEY)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(
        self,
        cycle_result: CycleResult,
        hypothesis: Hypothesis,
        problem: Problem,
        all_hypotheses: list[Hypothesis],
    ) -> CycleResult:
        """
        Apply the hypothesis as a PR and update cycle_result with the outcome.
        """
        if hypothesis.status != HypothesisStatus.APPROVED:
            raise ValueError(
                f"Cannot execute hypothesis '{hypothesis.id}': status is {hypothesis.status}"
            )

        logger.info("ExecutorAgent — generating code changes for '%s' …", hypothesis.title)
        file_changes = self._generate_changes(hypothesis)

        if not file_changes:
            logger.error("ExecutorAgent — LLM returned no file changes; aborting execution.")
            cycle_result.rejected = True
            cycle_result.rejection_reason = "Executor could not generate concrete file changes."
            return cycle_result

        is_safe, reason = self._validate_changes(file_changes, hypothesis, problem)
        if not is_safe:
            logger.warning("ExecutorAgent — blocked by safety gate: %s", reason)
            cycle_result.rejected = True
            cycle_result.rejection_reason = reason
            hypothesis.status = HypothesisStatus.REJECTED
            return cycle_result

        branch_name = self._make_branch_name(hypothesis)
        logger.info("ExecutorAgent — creating branch '%s' …", branch_name)
        self.github.create_branch(branch_name)

        logger.info("ExecutorAgent — committing %d file(s) …", len(file_changes))
        for change in file_changes:
            self.github.upsert_file(
                path=change["path"],
                content=change["content"],
                message=f"ai-factory: {hypothesis.title[:72]}",
                branch=branch_name,
            )

        pr_body = self._build_pr_body(problem, hypothesis, all_hypotheses)
        pr = self.github.create_pull_request(
            title=f"[AI Factory] {hypothesis.title}",
            body=pr_body,
            head=branch_name,
            labels=["ai-factory"],
        )

        cycle_result.pr_url = pr["html_url"]
        cycle_result.pr_number = pr["number"]
        hypothesis.status = HypothesisStatus.EXECUTED
        logger.info(
            "ExecutorAgent — PR #%s created: %s", pr["number"], pr["html_url"]
        )
        return cycle_result

    # ------------------------------------------------------------------
    # Code-change generation
    # ------------------------------------------------------------------

    def _generate_changes(self, hypothesis: Hypothesis) -> list[dict]:
        # If the hypothesis already contains proposed_changes, use them directly.
        if hypothesis.proposed_changes:
            return [
                {"path": path, "content": content}
                for path, content in hypothesis.proposed_changes.items()
            ]

        # Otherwise ask the LLM to generate them.
        current_contents: dict[str, str] = {}
        for path in hypothesis.files_to_modify:
            content = self.github.get_file_content(path)
            if content:
                current_contents[path] = content[: config.MAX_FILE_CHARS]

        user_message = (
            f"Hypothesis title: {hypothesis.title}\n"
            f"Approach: {hypothesis.approach}\n"
            f"Implementation plan:\n{hypothesis.implementation_plan}\n\n"
            "Current file contents:\n"
        )
        for path, content in current_contents.items():
            user_message += f"\n### {path}\n```\n{content}\n```\n"
        user_message += "\nGenerate the minimal file changes JSON array."

        response = self.ai.chat.completions.create(
            model=config.OPENAI_MODEL,
            temperature=0.2,
            max_tokens=config.OPENAI_MAX_TOKENS,
            messages=[
                {"role": "system", "content": self.CHANGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        raw = response.choices[0].message.content or "[]"
        return self._parse_changes(raw)

    def _parse_changes(self, raw: str) -> list[dict]:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            items = json.loads(raw)
            return [i for i in items if "path" in i and "content" in i]
        except json.JSONDecodeError as exc:
            logger.error("ExecutorAgent — failed to parse file changes: %s", exc)
            return []

    def _validate_changes(
        self,
        file_changes: list[dict],
        hypothesis: Hypothesis,
        problem: Problem,
    ) -> tuple[bool, str]:
        """Validate that generated changes are small, safe, and syntactically sound."""
        if len(file_changes) > config.MAX_FILES_PER_EXECUTION:
            return False, (
                f"Safety gate blocked execution: {len(file_changes)} files exceed the limit "
                f"of {config.MAX_FILES_PER_EXECUTION}."
            )

        allowed_files = set(hypothesis.files_to_modify) | set(problem.affected_files)
        seen_paths: set[str] = set()
        total_size = 0

        for change in file_changes:
            path = str(change.get("path", "")).replace("\\", "/").strip()
            content = change.get("content", "")

            if not path:
                return False, "Safety gate blocked execution: empty file path detected."
            if path.startswith("/") or ".." in PurePosixPath(path).parts:
                return False, f"Safety gate blocked execution: invalid path '{path}'."
            if path in seen_paths:
                return False, f"Safety gate blocked execution: duplicate path '{path}'."
            if not isinstance(content, str) or not content.strip():
                return False, f"Safety gate blocked execution: file '{path}' has empty content."
            if len(content) > config.MAX_FILE_CHANGE_SIZE:
                return False, (
                    f"Safety gate blocked execution: file '{path}' is too large "
                    f"({len(content)} chars)."
                )

            if allowed_files and path not in allowed_files and not self._is_related_path(path, allowed_files):
                return False, (
                    f"Safety gate blocked execution: unexpected file '{path}' was not present "
                    "in the approved implementation scope."
                )

            syntax_error = self._validate_syntax(path, content)
            if syntax_error:
                return False, f"Safety gate blocked execution: {syntax_error}"

            seen_paths.add(path)
            total_size += len(content)

        if total_size > config.MAX_TOTAL_CHANGE_SIZE:
            return False, (
                f"Safety gate blocked execution: total payload size {total_size} chars exceeds "
                f"the limit of {config.MAX_TOTAL_CHANGE_SIZE}."
            )

        return True, "ok"

    @staticmethod
    def _is_related_path(path: str, allowed_files: set[str]) -> bool:
        path_parts = PurePosixPath(path).parts[:-1]
        for allowed in allowed_files:
            allowed_parts = PurePosixPath(allowed.replace('\\', '/')).parts[:-1]
            if path_parts and path_parts == allowed_parts:
                return True
        return False

    @staticmethod
    def _validate_syntax(path: str, content: str) -> Optional[str]:
        suffix = PurePosixPath(path).suffix.lower()
        if suffix == ".py":
            try:
                ast.parse(content)
            except SyntaxError as exc:
                return f"python syntax error in '{path}': {exc.msg}"
        if suffix == ".json":
            try:
                json.loads(content)
            except json.JSONDecodeError as exc:
                return f"json syntax error in '{path}': {exc.msg}"
        return None

    # ------------------------------------------------------------------
    # Branch naming
    # ------------------------------------------------------------------

    def _make_branch_name(self, hypothesis: Hypothesis) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "-", hypothesis.title.lower()).strip("-")[:40]
        return f"{config.BRANCH_PREFIX}{timestamp}-{slug}"

    # ------------------------------------------------------------------
    # PR body
    # ------------------------------------------------------------------

    def _build_pr_body(
        self,
        problem: Problem,
        selected: Hypothesis,
        all_hypotheses: list[Hypothesis],
    ) -> str:
        discarded = [h for h in all_hypotheses if h.id != selected.id]

        lines: list[str] = [
            "## 🤖 AI Factory v2 — Automated Improvement",
            "",
            "This Pull Request was generated autonomously by AI Factory v2 "
            "following the hypothesis-comparison workflow.",
            "",
            "---",
            "",
            "## 📋 Detected Problem",
            "",
            f"**{problem.title}**",
            "",
            problem.description,
            "",
            f"- **Category:** {problem.category}",
            f"- **Priority:** {problem.priority}",
            f"- **Affected files:** {', '.join(problem.affected_files) or '_not specified_'}",
            "",
            "---",
            "",
            "## ✅ Selected Hypothesis",
            "",
            f"**{selected.title}**",
            "",
            f"*Approach:* {selected.approach}",
            "",
            selected.description,
            "",
            "### Implementation Plan",
            "",
            selected.implementation_plan,
            "",
        ]

        if selected.score:
            s = selected.score
            lines += [
                "### Scores",
                "",
                "| Criterion | Score |",
                "|-----------|-------|",
                f"| Business Impact | {s.business_impact} / 10 |",
                f"| Technical Risk | {s.technical_risk} / 10 |",
                f"| Complexity | {s.complexity} / 10 |",
                f"| Maintainability | {s.maintainability} / 10 |",
                f"| Scalability | {s.scalability} / 10 |",
                f"| **Composite** | **{s.composite:.2f} / 10** |",
                "",
                "### Final Decision Justification",
                "",
                selected.evaluation_rationale or "Selected because it best balanced value, safety, and maintainability.",
                "",
            ]

        if selected.critic_feedback:
            lines += [
                "### Critic Agent Feedback",
                "",
                selected.critic_feedback,
                "",
            ]
            if selected.critic_risks:
                lines += ["**Risks reviewed:**"] + [f"- {risk}" for risk in selected.critic_risks] + [""]

        if discarded:
            lines += [
                "---",
                "",
                "## ❌ Discarded Hypotheses",
                "",
            ]
            for h in discarded:
                lines.append(f"### {h.title}")
                lines.append(f"*Approach:* {h.approach}")
                if h.score:
                    lines.append(
                        f"*Composite score:* {h.score.composite:.2f} | "
                        f"Business Impact: {h.score.business_impact} | "
                        f"Risk: {h.score.technical_risk}"
                    )
                lines.append(f"*Status:* {h.status.value}")
                lines.append("")

        lines += [
            "---",
            "",
            "> *Generated by [AI Factory v2](../ai-factory-v2/specification.md) — "
            "autonomous engineering system.*",
        ]
        return "\n".join(lines)
