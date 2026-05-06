"""Lightweight GitHub API wrapper with graceful offline fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from github import Github
except ImportError:  # pragma: no cover
    Github = None


@dataclass
class PullRequestResult:
    url: str
    number: int


class GitHubClient:
    def __init__(self, config: Dict[str, Any]):
        token = config.get("token") or config.get("github_token")
        self.max_prs_per_run = int(config.get("max_prs_per_run", 10))
        self._client = Github(token) if (Github and token) else None

    async def create_pull_request(self, repo_name: str, title: str, body: str, head: str, base: str = "main") -> Optional[PullRequestResult]:
        if self._client is None:
            return None
        repo = self._client.get_repo(repo_name)
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return PullRequestResult(url=pr.html_url, number=pr.number)
