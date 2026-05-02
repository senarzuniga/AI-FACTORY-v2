"""GNAP coordinator using Git-tracked request/result files as coordination substrate."""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

try:
	import git
except ImportError:  # pragma: no cover
	git = None


class JobStatus(Enum):
	PENDING = "pending"
	ASSIGNED = "assigned"
	IN_PROGRESS = "in_progress"
	COMPLETED = "completed"
	FAILED = "failed"
	RETRY = "retry"


@dataclass
class GNAPJob:
	job_id: str
	repository: str
	action: str
	parameters: Dict[str, Any]
	status: JobStatus
	assigned_to: Optional[str] = None
	created_at: str = field(default_factory=lambda: datetime.now().isoformat())
	updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
	result: Optional[Dict[str, Any]] = None


class GNAPCoordinator:
	def __init__(self, repo_path: Path, config: Dict[str, Any]):
		self.repo_path = repo_path
		self.config = config
		self.gnap_root = repo_path / "gnap"
		self.requests_dir = self.gnap_root / "requests"
		self.results_dir = self.gnap_root / "results"
		self.manifest_file = self.gnap_root / "manifest.json"
		self._initialize_gnap()

	def _initialize_gnap(self) -> None:
		self.gnap_root.mkdir(exist_ok=True)
		self.requests_dir.mkdir(exist_ok=True)
		self.results_dir.mkdir(exist_ok=True)
		if not self.manifest_file.exists():
			manifest = {
				"version": "1.0",
				"protocol": "GNAP",
				"agents": [],
				"jobs": {},
				"created_at": datetime.now().isoformat(),
			}
			self.manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

	async def submit_job(self, repository: str, action: str, parameters: Dict[str, Any]) -> str:
		job_id = self._generate_job_id(repository, action, parameters)
		job = GNAPJob(job_id=job_id, repository=repository, action=action, parameters=parameters, status=JobStatus.PENDING)

		job_file = self.requests_dir / f"{job_id}.json"
		job_file.write_text(json.dumps(self._job_to_dict(job), indent=2), encoding="utf-8")
		await self._update_manifest(job_id, "submitted")
		await self._git_commit(f"GNAP submit {job_id}")
		return job_id

	async def claim_job(self, agent_id: str, agent_capabilities: List[str]) -> Optional[GNAPJob]:
		for job_file in sorted(self.requests_dir.glob("*.json")):
			data = json.loads(job_file.read_text(encoding="utf-8"))
			if data.get("status") not in {JobStatus.PENDING.value, JobStatus.RETRY.value}:
				continue
			if data.get("action") not in agent_capabilities:
				continue

			data["status"] = JobStatus.ASSIGNED.value
			data["assigned_to"] = agent_id
			data["updated_at"] = datetime.now().isoformat()
			job_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

			await self._update_manifest(data["job_id"], "assigned", agent_id)
			await self._git_commit(f"GNAP assign {data['job_id']} to {agent_id}")
			return self._dict_to_job(data)
		return None

	async def complete_job(self, job_id: str, result: Dict[str, Any], success: bool) -> bool:
		job_file = self.requests_dir / f"{job_id}.json"
		if not job_file.exists():
			return False

		data = json.loads(job_file.read_text(encoding="utf-8"))
		data["status"] = JobStatus.COMPLETED.value if success else JobStatus.FAILED.value
		data["result"] = result
		data["updated_at"] = datetime.now().isoformat()
		job_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

		result_file = self.results_dir / f"{job_id}_result.json"
		result_file.write_text(
			json.dumps(
				{
					"job_id": job_id,
					"result": result,
					"completed_at": datetime.now().isoformat(),
					"success": success,
				},
				indent=2,
			),
			encoding="utf-8",
		)

		await self._update_manifest(job_id, "completed" if success else "failed", data.get("assigned_to"))
		await self._git_commit(f"GNAP complete {job_id}")
		return True

	async def get_pending_jobs(self, repository: Optional[str] = None) -> List[GNAPJob]:
		jobs: List[GNAPJob] = []
		for job_file in self.requests_dir.glob("*.json"):
			data = json.loads(job_file.read_text(encoding="utf-8"))
			if data.get("status") in {JobStatus.PENDING.value, JobStatus.RETRY.value}:
				if repository is None or data.get("repository") == repository:
					jobs.append(self._dict_to_job(data))
		return jobs

	async def retry_failed_job(self, job_id: str) -> bool:
		job_file = self.requests_dir / f"{job_id}.json"
		if not job_file.exists():
			return False

		data = json.loads(job_file.read_text(encoding="utf-8"))
		if data.get("status") != JobStatus.FAILED.value:
			return False

		data["status"] = JobStatus.RETRY.value
		data["assigned_to"] = None
		data["result"] = None
		data["updated_at"] = datetime.now().isoformat()
		job_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
		await self._update_manifest(job_id, "retry")
		await self._git_commit(f"GNAP retry {job_id}")
		return True

	async def register_agent(self, agent_id: str, capabilities: List[str], endpoint: str) -> None:
		manifest = self._load_manifest()
		manifest.setdefault("agents", []).append(
			{
				"agent_id": agent_id,
				"capabilities": capabilities,
				"endpoint": endpoint,
				"registered_at": datetime.now().isoformat(),
				"status": "active",
			}
		)
		self._save_manifest(manifest)

	async def start_worker_pool(
		self,
		workers: int = 2,
		processor: Optional[Callable[[GNAPJob], Awaitable[Dict[str, Any]]]] = None,
		once: bool = True,
	) -> None:
		async def process(worker_id: int) -> None:
			agent_id = f"gnap-worker-{worker_id}"
			capabilities = ["apply_improvement", "analyze_repository"]
			await self.register_agent(agent_id, capabilities, endpoint="local")

			while True:
				job = await self.claim_job(agent_id, capabilities)
				if not job:
					if once:
						return
					await asyncio.sleep(1)
					continue

				try:
					payload = (
						await processor(job)
						if processor
						else {
							"message": "Processed by default GNAP worker",
							"job_id": job.job_id,
							"action": job.action,
						}
					)
					await self.complete_job(job.job_id, payload, success=True)
				except Exception as exc:  # noqa: BLE001
					await self.complete_job(job.job_id, {"error": str(exc)}, success=False)

				if once:
					return

		await asyncio.gather(*(process(i + 1) for i in range(max(1, workers))))

	def _generate_job_id(self, repository: str, action: str, parameters: Dict[str, Any]) -> str:
		raw = f"{repository}:{action}:{json.dumps(parameters, sort_keys=True)}:{datetime.now().isoformat()}"
		return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

	def _job_to_dict(self, job: GNAPJob) -> Dict[str, Any]:
		payload = asdict(job)
		payload["status"] = job.status.value
		return payload

	def _dict_to_job(self, data: Dict[str, Any]) -> GNAPJob:
		return GNAPJob(
			job_id=data["job_id"],
			repository=data["repository"],
			action=data["action"],
			parameters=data.get("parameters", {}),
			status=JobStatus(data["status"]),
			assigned_to=data.get("assigned_to"),
			created_at=data.get("created_at", datetime.now().isoformat()),
			updated_at=data.get("updated_at", datetime.now().isoformat()),
			result=data.get("result"),
		)

	async def _update_manifest(self, job_id: str, status_update: str, agent_id: Optional[str] = None) -> None:
		manifest = self._load_manifest()
		manifest.setdefault("jobs", {})[job_id] = {
			"status": status_update,
			"last_updated": datetime.now().isoformat(),
			"agent": agent_id,
		}
		self._save_manifest(manifest)

	def _load_manifest(self) -> Dict[str, Any]:
		return json.loads(self.manifest_file.read_text(encoding="utf-8"))

	def _save_manifest(self, manifest: Dict[str, Any]) -> None:
		self.manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

	async def _git_commit(self, message: str) -> None:
		if git is None:
			return
		try:
			repo = git.Repo(self.repo_path)
			repo.index.add([str(self.gnap_root)])
			if repo.is_dirty(index=True, working_tree=True, untracked_files=True):
				repo.index.commit(message)
		except Exception:
			return
