"""
AI Factory v2 — Configuration
"""
from __future__ import annotations

import os


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------
GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOSITORY: str = os.environ.get("GITHUB_REPOSITORY", "")  # owner/repo

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
MIN_BUSINESS_IMPACT: float = 7.0
MAX_TECHNICAL_RISK: float = 4.0

# ---------------------------------------------------------------------------
# Branch naming
# ---------------------------------------------------------------------------
BRANCH_PREFIX: str = "ai-factory/"

# ---------------------------------------------------------------------------
# Supabase (optional — set both vars to enable remote persistence)
# ---------------------------------------------------------------------------
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")

# ---------------------------------------------------------------------------
# Learning registry
# ---------------------------------------------------------------------------
LEARNING_FILE: str = "ai-factory-v2/learning/history.json"

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
