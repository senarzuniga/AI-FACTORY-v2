
"""
AI Factory v2 — Configuration
"""
from __future__ import annotations

from decouple import config
from pathlib import Path
from pydantic import BaseModel, ValidationError


class Config(BaseModel):
    GITHUB_TOKEN: str = config("GITHUB_TOKEN", default="")
    GITHUB_REPOSITORY: str = config("GITHUB_REPOSITORY", default="ALL")
    SKIP_REPOS: list[str] = [
        r.strip() for r in config("SKIP_REPOS", default="").split(",") if r.strip()
    ]
    SKIP_FORKS: bool = config("SKIP_FORKS", default="true").lower() == "true"
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", default="")
    OPENAI_MODEL: str = config("AI_MODEL", default="gpt-4o")
    OPENAI_MAX_TOKENS: int = config("AI_MAX_TOKENS", cast=int, default=4096)
    OPENAI_TEMPERATURE: float = config("AI_TEMPERATURE", cast=float, default=0.3)
    MIN_HYPOTHESES: int = 2
    MAX_HYPOTHESES: int = 5
    MIN_BUSINESS_IMPACT: float = config("MIN_BUSINESS_IMPACT", cast=float, default=7.0)
    MAX_TECHNICAL_RISK: float = config("MAX_TECHNICAL_RISK", cast=float, default=4.0)
    MIN_MAINTAINABILITY: float = config("MIN_MAINTAINABILITY", cast=float, default=5.0)
    MIN_SCALABILITY: float = config("MIN_SCALABILITY", cast=float, default=5.0)
    MIN_COMPOSITE_SCORE: float = config("MIN_COMPOSITE_SCORE", cast=float, default=6.5)
    MAX_COMPLEXITY: float = config("MAX_COMPLEXITY", cast=float, default=7.0)
    BRANCH_PREFIX: str = "ai-factory/"
    SUPABASE_URL: str = config("SUPABASE_URL", default="")
    SUPABASE_KEY: str = config("SUPABASE_KEY", default="")
    APP_DIR: Path = Path(__file__).resolve().parent
    LEARNING_FILE: str = str(APP_DIR / "learning" / "history.json")
    OUTPUT_DIR: str = str(APP_DIR / "output" / "cycles")
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
    MAX_FILE_CHARS: int = 8_000
    MAX_REPO_CHARS: int = 60_000


try:
    config = Config()
except ValidationError as e:
    print("Configuration validation error:", e)
    raise
