"""
AI Factory v2 — Configuration
"""
from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------
GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
# Set to a specific "owner/repo" to target one repository.
# Set to "ALL" (or leave empty) to analyse every repo you own.
GITHUB_REPOSITORY: str = os.environ.get("GITHUB_REPOSITORY", "ALL")

# Repos to skip in ALL mode (comma-separated, e.g. "owner/repo1,owner/repo2")
SKIP_REPOS: list[str] = [
    r.strip() for r in os.environ.get("SKIP_REPOS", "").split(",") if r.strip()
]

# Whether to skip forked repositories in ALL mode
SKIP_FORKS: bool = os.environ.get("SKIP_FORKS", "true").lower() == "true"

# ---------------------------------------------------------------------------
# AI / LLM
# ---------------------------------------------------------------------------
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.environ.get("AI_MODEL", "gpt-4o")
OPENAI_MAX_TOKENS: int = int(os.environ.get("AI_MAX_TOKENS", "4096"))
OPENAI_TEMPERATURE: float = float(os.environ.get("AI_TEMPERATURE", "0.3"))

# ---------------------------------------------------------------------------
# Hypothesis Engineering
# ---------------------------------------------------------------------------
MIN_HYPOTHESES: int = 2
MAX_HYPOTHESES: int = 5

# ---------------------------------------------------------------------------
# Scoring thresholds (Execution Rule)
# ---------------------------------------------------------------------------
MIN_BUSINESS_IMPACT: float = float(os.environ.get("MIN_BUSINESS_IMPACT", "7.0"))
MAX_TECHNICAL_RISK: float = float(os.environ.get("MAX_TECHNICAL_RISK", "4.0"))
MIN_MAINTAINABILITY: float = float(os.environ.get("MIN_MAINTAINABILITY", "5.0"))
MIN_SCALABILITY: float = float(os.environ.get("MIN_SCALABILITY", "5.0"))
MIN_COMPOSITE_SCORE: float = float(os.environ.get("MIN_COMPOSITE_SCORE", "6.5"))
MAX_COMPLEXITY: float = float(os.environ.get("MAX_COMPLEXITY", "7.0"))

# ---------------------------------------------------------------------------
# Branch naming
# ---------------------------------------------------------------------------
BRANCH_PREFIX: str = "ai-factory/"

# ---------------------------------------------------------------------------
# Dry-run mode (analyse and score only — no PR creation)
# ---------------------------------------------------------------------------
DRY_RUN: bool = os.environ.get("DRY_RUN", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Execution safety gates
# ---------------------------------------------------------------------------
MAX_FILES_PER_EXECUTION: int = int(os.environ.get("MAX_FILES_PER_EXECUTION", "5"))
MAX_FILE_CHANGE_SIZE: int = int(os.environ.get("MAX_FILE_CHANGE_SIZE", "20000"))
MAX_TOTAL_CHANGE_SIZE: int = int(os.environ.get("MAX_TOTAL_CHANGE_SIZE", "60000"))

# ---------------------------------------------------------------------------
# Learning registry
# ---------------------------------------------------------------------------
APP_DIR: Path = Path(__file__).resolve().parent
LEARNING_FILE: str = str(APP_DIR / "learning" / "history.json")
OUTPUT_DIR: str = str(APP_DIR / "output" / "cycles")

# ---------------------------------------------------------------------------
# Analysed file extensions
# ---------------------------------------------------------------------------
ANALYSED_EXTENSIONS: tuple[str, ...] = (
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".java",
    ".rb",
    ".rs",
    ".c",
    ".cpp",
    ".cs",
    ".php",
    ".swift",
    ".kt",
    ".yml",
    ".yaml",
    ".json",
    ".md",
)

# Directories to skip during analysis
SKIP_DIRS: tuple[str, ...] = (
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    "coverage",
    ".coverage",
)

# Maximum characters of file content sent to the AI (per file)
MAX_FILE_CHARS: int = 8_000

# Maximum total characters for the repository snapshot
MAX_REPO_CHARS: int = 60_000
