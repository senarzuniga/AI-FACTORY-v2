
"""
AI Factory v2 — Configuration
"""
from __future__ import annotations

from decouple import config
from pathlib import Path


def _resolve_openai_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if api_key:
        return api_key

    try:
        from openai_key_manager import setup_openai_env
    except Exception:
        return ""

    try:
        setup_openai_env()
    except Exception:
        return ""

    return os.environ.get("OPENAI_API_KEY", "").strip()


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

# Optional owner/org filter in ALL mode (comma-separated, e.g. "my-user,my-org")
TARGET_OWNERS: list[str] = [
    o.strip().lower() for o in os.environ.get("TARGET_OWNERS", "").split(",") if o.strip()
]

# Optional cap for multi-repo runs to limit rollout size; 0 means unlimited.
MAX_REPOS_PER_RUN: int = int(os.environ.get("MAX_REPOS_PER_RUN", "0"))

# Whether to skip forked repositories in ALL mode
SKIP_FORKS: bool = os.environ.get("SKIP_FORKS", "true").lower() == "true"

# ---------------------------------------------------------------------------
# AI / LLM
# ---------------------------------------------------------------------------
OPENAI_API_KEY: str = _resolve_openai_api_key()
OPENAI_MODEL: str = os.environ.get("AI_MODEL", "gpt-4o")
# Reduced default: shorter responses → faster LLM round-trips.
OPENAI_MAX_TOKENS: int = int(os.environ.get("AI_MAX_TOKENS", "2048"))
OPENAI_TEMPERATURE: float = float(os.environ.get("AI_TEMPERATURE", "0.3"))

# ---------------------------------------------------------------------------
# Hypothesis Engineering
# Fast mode: MIN=MAX=2 to produce the fewest LLM calls while still satisfying
# the mandatory diversity gate.  Override with MAX_HYPOTHESES env var.
# ---------------------------------------------------------------------------
MIN_HYPOTHESES: int = 2
MAX_HYPOTHESES: int = int(os.environ.get("MAX_HYPOTHESES", "2"))

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
API_RETRY_ATTEMPTS: int = int(os.environ.get("API_RETRY_ATTEMPTS", "3"))
# Shorter backoff between retries — still safe for 429/5xx handling.
API_RETRY_BACKOFF_SECONDS: float = float(os.environ.get("API_RETRY_BACKOFF_SECONDS", "0.3"))

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

# Reduced per-file and total snapshot sizes → smaller prompts → faster LLM responses.
MAX_FILE_CHARS: int = int(os.environ.get("MAX_FILE_CHARS", "4_000"))
MAX_REPO_CHARS: int = int(os.environ.get("MAX_REPO_CHARS", "30_000"))
