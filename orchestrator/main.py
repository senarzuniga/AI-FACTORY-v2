"""AI-FACTORY-v2 advanced orchestrator integrating protocol modules."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from orchestrator.agents.critic_agent import CriticAgent
from orchestrator.agents.grounding_agent import GroundingAgent
from orchestrator.agents.optimizer_agent import OptimizerAgent
from orchestrator.agents.planning_agent import PlanningAgent
from orchestrator.core.coepg_trainer import CoEPGTrainer
from orchestrator.core.epoch_protocol import EpochProtocol
from orchestrator.core.escher_loop import EscherLoop
from orchestrator.core.gnap_coordinator import GNAPCoordinator
from orchestrator.core.imcts_engine import IMCTSEngine
from orchestrator.memory.experience_replay import ExperienceReplay
from orchestrator.memory.vector_store import VectorStore
from orchestrator.utils.github_client import GitHubClient
from orchestrator.utils.logger import get_logger

logger = get_logger(__name__)


class AIFactoryV2:
    def __init__(self, config: Dict[str, Any], work_dir: Path):
        self.config = config
        self.work_dir = work_dir

        data_dir = self.work_dir / self.config["orchestrator"].get("data_dir", ".ai-factory")
        data_dir.mkdir(parents=True, exist_ok=True)

        self.epoch = EpochProtocol(self.config["protocols"]["epoch"], data_dir)
        self.imcts = IMCTSEngine(self.config["protocols"]["imcts"])
        self.escher = EscherLoop(self.config["protocols"]["escher_loop"], data_dir / "escher")
        self.gnap = GNAPCoordinator(self.work_dir, self.config["protocols"]["gnap"])
        self.coepg = CoEPGTrainer(self.config["protocols"]["coepg"])

        self.github = GitHubClient(self.config.get("github", {}))
        self.planning_agent = PlanningAgent(self.config["agents"]["planning"])
        self.grounding_agent = GroundingAgent(self.config["agents"]["grounding"], self.work_dir)
        self.critic_agent = CriticAgent(self.config["agents"]["critic"])
        self.optimizer_agent = OptimizerAgent(self.config["agents"]["optimizer"])

        mem_cfg = self.config["memory"]
        self.vector_store = VectorStore(dimension=int(mem_cfg["vector_store"].get("dimension", 1536)))
        self.replay = ExperienceReplay(
            capacity=int(mem_cfg["experience_replay"].get("capacity", 10000)),
            prioritized=bool(mem_cfg["experience_replay"].get("priority", True)),
        )

    async def run(self, repository_url: Optional[str] = None) -> Dict[str, Any]:
        initial_metrics = await self._gather_metrics()
        await self.epoch.establish_baseline(initial_metrics)
        round_id = await self.epoch.start_optimization_round({"repository_url": repository_url})

        analysis = await self._analyze_repository(repository_url)
        hypotheses = await self._generate_hypotheses_with_imcts(analysis)

        validated: List[Dict[str, Any]] = []
        for hypothesis in hypotheses:
            verdict = await self.critic_agent.validate(hypothesis)
            if verdict["score"] >= float(self.config["protocols"]["epoch"].get("baseline_threshold", 0.85)):
                hypothesis["critic"] = verdict
                validated.append(hypothesis)

        result: Dict[str, Any] = {"applied": [], "failed": [], "status": "no_valid_hypothesis"}
        if validated:
            best = max(validated, key=lambda h: h["critic"]["score"])
            result = await self._execute_hypothesis(best)

            new_metrics = await self._gather_metrics(result)
            improved = await self.epoch.record_improvement(
                round_id,
                "overall_score",
                float(initial_metrics.get("overall_score", 0.0)),
                float(new_metrics.get("overall_score", 0.0)),
            )

            if improved and self.config["protocols"]["escher_loop"].get("enabled", True):
                await self._evolve_agents()

            if self.config["protocols"]["gnap"].get("enabled", True):
                await self._submit_to_gnap(result)

            coepg_stats = self.coepg.update(
                planning_success=1.0 if result.get("applied") else 0.4,
                grounding_success=1.0 if not result.get("failed") else 0.5,
                critic_score=float(best["critic"]["score"]),
            )
            result["coepg"] = coepg_stats

            await self.epoch.complete_round(round_id, new_metrics)
        else:
            await self.epoch.complete_round(round_id, initial_metrics)

        return result

    async def _generate_hypotheses_with_imcts(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        async def evaluate_state(state: Dict[str, Any]) -> float:
            score = 0.7
            if state.get("last_action", {}).get("type") == "add_tests":
                score += 0.1
            return min(1.0, score)

        best_action = await self.imcts.search(
            initial_state={"analysis": analysis, "depth": 0},
            evaluation_fn=evaluate_state,
            max_iterations=int(self.config["protocols"]["imcts"].get("max_iterations", 100)),
        )
        return [
            {
                "title": "IMCTS selected action",
                "description": "Action chosen via introspective search",
                "analysis": analysis,
                "constraints": {"risk_tolerance": "medium"},
                "action": best_action,
            }
        ]

    async def _execute_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        plan = await self.planning_agent.generate_plan(hypothesis.get("analysis", {}), hypothesis.get("constraints", {}))
        changes, feedback = await self.grounding_agent.ground_plan(plan)

        if not feedback.get("successful", True):
            plan = await self.planning_agent.refine_plan(plan, feedback)
            changes, feedback = await self.grounding_agent.ground_plan(plan)

        dry_run = self.config["orchestrator"].get("mode", "production") == "dry-run"
        result = await self.grounding_agent.apply_changes(changes, dry_run=dry_run)
        result["status"] = "dry_run" if dry_run else "executed"
        return result

    async def _evolve_agents(self) -> None:
        async def task_eval(genome: Any) -> float:
            return 0.7 + float(genome.dna.get("creativity", 0.3)) * 0.2

        async def optimizer_eval(genome: Any, _: List[Any]) -> float:
            return 0.65 + float(genome.dna.get("evolution_rate", 0.1)) * 0.2

        await self.escher.evolve_mutual(task_eval, optimizer_eval, generations=3)

    async def _submit_to_gnap(self, result: Dict[str, Any]) -> None:
        await self.gnap.submit_job(
            repository="ALL",
            action="apply_improvement",
            parameters={"changes": result.get("applied", [])},
        )

    async def _gather_metrics(self, execution_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        score = 0.75
        if execution_result and execution_result.get("applied"):
            score += 0.08
        return {
            "overall_score": score,
            "test_coverage": 0.70,
            "complexity_score": 0.65,
            "timestamp": datetime.now().isoformat(),
        }

    async def _analyze_repository(self, repository_url: Optional[str]) -> Dict[str, Any]:
        _ = repository_url
        return {
            "structure": {"root": str(self.work_dir)},
            "issues": [],
            "opportunities": ["incremental hardening", "targeted tests"],
            "candidate_files": ["README.md"],
        }


async def run_from_config(config: Dict[str, Any]) -> Dict[str, Any]:
    orchestrator = AIFactoryV2(config=config, work_dir=Path.cwd())
    result = await orchestrator.run()
    if config["protocols"]["gnap"].get("enabled", True):
        await orchestrator.gnap.start_worker_pool(workers=2, once=True)
    return result
