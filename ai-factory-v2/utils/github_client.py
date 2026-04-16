"""
AI Factory v2 — GitHub API client wrapper
"""
from __future__ import annotations

import base64
import json
import time
from datetime import datetime
from typing import Optional

import requests

import config
from utils.logger import get_logger

logger = get_logger(__name__)


class GitHubClient:
    """Thin wrapper around the GitHub REST API v3."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, repository: str) -> None:
        if not token:
            raise ValueError("GITHUB_TOKEN is required")
        if not repository or "/" not in repository:
            raise ValueError("GITHUB_REPOSITORY must be 'owner/repo'")
        self.token = token
        self.repository = repository
        self.owner, self.repo = repository.split("/", 1)
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self.BASE_URL}{path}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._url(path)
        last_error: Optional[Exception] = None
        for attempt in range(1, config.API_RETRY_ATTEMPTS + 1):
            try:
                response = self._session.request(method, url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                should_retry = status_code in {429, 500, 502, 503, 504} or status_code is None
                if attempt >= config.API_RETRY_ATTEMPTS or not should_retry:
                    raise
                delay = config.API_RETRY_BACKOFF_SECONDS * attempt
                logger.warning(
                    "GitHub API %s %s failed on attempt %d/%d (%s). Retrying in %.1fs.",
                    method.upper(),
                    path,
                    attempt,
                    config.API_RETRY_ATTEMPTS,
                    exc,
                    delay,
                )
                time.sleep(delay)
        assert last_error is not None
        raise last_error

    def _get(self, path: str, **kwargs) -> dict | list:
        response = self._request("get", path, **kwargs)
        return response.json()

    def _post(self, path: str, payload: dict) -> dict:
        response = self._request("post", path, json=payload)
        return response.json()

    def _put(self, path: str, payload: dict) -> dict:
        response = self._request("put", path, json=payload)
        return response.json()

    # ------------------------------------------------------------------
    # Repository
    # ------------------------------------------------------------------

    def get_default_branch(self) -> str:
        data = self._get(f"/repos/{self.owner}/{self.repo}")
        return data.get("default_branch", "main")

    def get_branch_sha(self, branch: str) -> str:
        data = self._get(
            f"/repos/{self.owner}/{self.repo}/git/ref/heads/{branch}"
        )
        return data["object"]["sha"]

    def get_tree(self, tree_sha: str) -> list[dict]:
        data = self._get(
            f"/repos/{self.owner}/{self.repo}/git/trees/{tree_sha}",
            params={"recursive": "1"},
        )
        return data.get("tree", [])

    def get_file_content(self, path: str, ref: Optional[str] = None) -> Optional[str]:
        """Return decoded file content or None if the file does not exist."""
        params = {}
        if ref:
            params["ref"] = ref
        try:
            data = self._get(
                f"/repos/{self.owner}/{self.repo}/contents/{path}",
                params=params,
            )
            if isinstance(data, dict) and data.get("encoding") == "base64":
                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            raise
        return None

    def list_repo_files(self, ref: Optional[str] = None) -> list[str]:
        """Return a list of all file paths in the repository."""
        branch = ref or self.get_default_branch()
        sha = self.get_branch_sha(branch)
        tree = self.get_tree(sha)
        return [item["path"] for item in tree if item["type"] == "blob"]

    # ------------------------------------------------------------------
    # Branches
    # ------------------------------------------------------------------

    def create_branch(self, branch_name: str, from_branch: Optional[str] = None) -> str:
        """Create a new branch and return the SHA it points to."""
        base = from_branch or self.get_default_branch()
        sha = self.get_branch_sha(base)
        self._post(
            f"/repos/{self.owner}/{self.repo}/git/refs",
            {"ref": f"refs/heads/{branch_name}", "sha": sha},
        )
        logger.info("Created branch '%s' from '%s' (%s)", branch_name, base, sha[:7])
        return sha

    # ------------------------------------------------------------------
    # Commits / file updates
    # ------------------------------------------------------------------

    def upsert_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str,
    ) -> dict:
        """Create or update a file on a branch and return the commit data."""
        encoded = base64.b64encode(content.encode()).decode()
        payload: dict = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }
        # If file already exists we need to send its SHA
        try:
            existing = self._get(
                f"/repos/{self.owner}/{self.repo}/contents/{path}",
                params={"ref": branch},
            )
            if isinstance(existing, dict) and "sha" in existing:
                payload["sha"] = existing["sha"]
        except requests.HTTPError as exc:
            if exc.response is None or exc.response.status_code != 404:
                raise
        result = self._put(
            f"/repos/{self.owner}/{self.repo}/contents/{path}",
            payload,
        )
        logger.info("Upserted file '%s' on branch '%s'", path, branch)
        return result

    # ------------------------------------------------------------------
    # Pull Requests
    # ------------------------------------------------------------------

    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> dict:
        """Open a Pull Request and return its data dict."""
        base_branch = base or self.get_default_branch()
        payload: dict = {
            "title": title,
            "body": body,
            "head": head,
            "base": base_branch,
        }
        pr = self._post(f"/repos/{self.owner}/{self.repo}/pulls", payload)
        logger.info("Opened PR #%s: %s", pr["number"], pr["html_url"])
        if labels:
            self._add_labels(pr["number"], labels)
        return pr

    def get_pull_request(self, pr_number: int) -> dict:
        """Fetch a pull request by number and return its API payload."""
        data = self._get(f"/repos/{self.owner}/{self.repo}/pulls/{pr_number}")
        if not isinstance(data, dict):
            raise ValueError(f"Unexpected PR response for #{pr_number}")
        return data

    def _add_labels(self, pr_number: int, labels: list[str]) -> None:
        try:
            self._post(
                f"/repos/{self.owner}/{self.repo}/issues/{pr_number}/labels",
                {"labels": labels},
            )
        except requests.HTTPError:
            logger.warning("Could not add labels to PR #%s (they may not exist)", pr_number)

    # ------------------------------------------------------------------
    # Multi-repo discovery
    # ------------------------------------------------------------------

    @classmethod
    def discover_repos(
        cls,
        token: str,
        skip_archived: bool = True,
        skip_forks: bool = False,
    ) -> list[str]:
        """
        Return all 'owner/repo' strings accessible with the given token.
        Only repos where the authenticated user is the owner are returned.
        Handles GitHub pagination automatically.
        """
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        repos: list[str] = []
        page = 1
        while True:
            resp = session.get(
                f"{cls.BASE_URL}/user/repos",
                params={"per_page": 100, "page": page, "affiliation": "owner", "sort": "updated"},
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            for r in batch:
                if skip_archived and r.get("archived"):
                    continue
                if skip_forks and r.get("fork"):
                    continue
                repos.append(r["full_name"])
            if len(batch) < 100:
                break
            page += 1
        logger.info("Discovered %d repository/repositories for the authenticated user", len(repos))
        return repos
