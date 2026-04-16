"""
AI Factory v2 — Data models
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").strip().lower()).strip()


def normalize_category(value: str) -> str:
    text = _normalize_text(value)
    if any(token in text for token in ("security", "auth", "permission", "secret")):
        return "security"
    if any(token in text for token in ("perform", "optim", "scal")):
        return "performance"
    if any(token in text for token in ("architect", "refactor", "design", "structure")):
        return "architecture"
    if any(token in text for token in ("maint", "readab", "cleanup", "quality")):
        return "maintainability"
    if any(token in text for token in ("test", "coverage", "assert")):
        return "testing"
    if any(token in text for token in ("doc", "readme", "comment")):
        return "documentation"
    return text or "general"


def normalize_priority(value: str) -> str:
    text = _normalize_text(value)
    if "critical" in text or text == "p0":
        return "critical"
    if "high" in text or text == "p1":
        return "high"
    if "low" in text or text == "p3":
        return "low"
    return "medium"


def normalize_approach(value: str) -> str:
    text = _normalize_text(value)
    if any(token in text for token in ("algorithm", "optim", "cache")):
        return "algorithm optimization"
    if any(token in text for token in ("refactor", "architect", "pattern", "module")):
        return "architecture refactor"
    if any(token in text for token in ("simpl", "streamline", "cleanup")):
        return "logic simplification"
    if any(token in text for token in ("guard", "validate", "safety", "reliab")):
        return "reliability hardening"
    if any(token in text for token in ("depend", "library", "service")):
        return "dependency strategy"
    return text or "general"


class HypothesisStatus(str, Enum):
    PENDING = "pending"
    EVALUATED = "evaluated"
    SELECTED = "selected"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


@dataclass
class HypothesisScore:
    """Scoring for a single hypothesis across all five evaluation criteria."""

    business_impact: float = 0.0    # 0–10  (higher is better)
    technical_risk: float = 0.0     # 0–10  (lower is better)
    complexity: float = 0.0         # 0–10  (lower is better)
    maintainability: float = 0.0    # 0–10  (higher is better)
    scalability: float = 0.0        # 0–10  (higher is better)

    @property
    def composite(self) -> float:
        """
        Composite score based on the spec formula:

            score = (
                business_impact * 2.0
                + (10 - technical_risk) * 1.5
                + (10 - complexity)     * 0.5
                + maintainability       * 1.0
                + scalability           * 1.0
            ) / 6.0
        """
        return (
            self.business_impact * 2.0
            + (10.0 - self.technical_risk) * 1.5
            + (10.0 - self.complexity) * 0.5
            + self.maintainability * 1.0
            + self.scalability * 1.0
        ) / 6.0

    def to_dict(self) -> dict:
        return {
            "business_impact": self.business_impact,
            "technical_risk": self.technical_risk,
            "complexity": self.complexity,
            "maintainability": self.maintainability,
            "scalability": self.scalability,
            "composite": round(self.composite, 2),
        }


@dataclass
class Hypothesis:
    """A single candidate solution for a detected problem."""

    id: str
    problem_id: str
    title: str
    description: str
    approach: str                            # structural approach label
    implementation_plan: str                 # step-by-step textual plan
    files_to_modify: list[str] = field(default_factory=list)
    proposed_changes: dict[str, str] = field(default_factory=dict)  # path -> new content
    score: Optional[HypothesisScore] = None
    status: HypothesisStatus = HypothesisStatus.PENDING
    critic_feedback: Optional[str] = None
    critic_risks: list[str] = field(default_factory=list)
    evaluation_rationale: Optional[str] = None

    def __post_init__(self) -> None:
        self.approach = normalize_approach(self.approach)
        if isinstance(self.implementation_plan, list):
            self.implementation_plan = "\n".join(
                f"{idx + 1}. {step}" for idx, step in enumerate(self.implementation_plan)
            )
        if isinstance(self.files_to_modify, str):
            self.files_to_modify = [self.files_to_modify]
        self.files_to_modify = list(dict.fromkeys(self.files_to_modify))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "title": self.title,
            "description": self.description,
            "approach": self.approach,
            "implementation_plan": self.implementation_plan,
            "files_to_modify": self.files_to_modify,
            "score": self.score.to_dict() if self.score else None,
            "status": self.status.value,
            "critic_feedback": self.critic_feedback,
            "critic_risks": self.critic_risks,
            "evaluation_rationale": self.evaluation_rationale,
        }


@dataclass
class Problem:
    """An identified improvement opportunity inside the repository."""

    id: str
    title: str
    description: str
    category: str          # architecture | performance | security | maintainability | …
    affected_files: list[str] = field(default_factory=list)
    priority: str = "medium"   # low | medium | high | critical

    def __post_init__(self) -> None:
        self.category = normalize_category(self.category)
        self.priority = normalize_priority(self.priority)
        if isinstance(self.affected_files, str):
            self.affected_files = [self.affected_files]
        self.affected_files = list(dict.fromkeys(self.affected_files))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "affected_files": self.affected_files,
            "priority": self.priority,
        }


@dataclass
class RepositoryAnalysis:
    """Structured analysis context generated by the Analyzer Agent."""

    repository_summary: str = ""
    architecture_notes: list[str] = field(default_factory=list)
    improvement_opportunities: list[str] = field(default_factory=list)
    repo_context: str = ""
    problems: list[Problem] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "repository_summary": self.repository_summary,
            "architecture_notes": self.architecture_notes,
            "improvement_opportunities": self.improvement_opportunities,
            "repo_context": self.repo_context,
            "problems": [p.to_dict() for p in self.problems],
        }


@dataclass
class CycleResult:
    """Outcome of a complete AI Factory orchestration cycle."""

    cycle_id: str
    repository: str
    problems: list[Problem] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    selected_hypothesis: Optional[Hypothesis] = None
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    rejected: bool = False
    rejection_reason: Optional[str] = None
    analysis_summary: str = ""
    analysis_notes: list[str] = field(default_factory=list)
    decision_log: list[dict] = field(default_factory=list)
    report_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "cycle_id": self.cycle_id,
            "repository": self.repository,
            "analysis_summary": self.analysis_summary,
            "analysis_notes": self.analysis_notes,
            "decision_log": self.decision_log,
            "problems": [p.to_dict() for p in self.problems],
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "selected_hypothesis": (
                self.selected_hypothesis.to_dict()
                if self.selected_hypothesis
                else None
            ),
            "pr_url": self.pr_url,
            "pr_number": self.pr_number,
            "rejected": self.rejected,
            "rejection_reason": self.rejection_reason,
            "report_path": self.report_path,
        }
