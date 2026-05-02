"""Escher-Loop mutual evolution engine for task and optimizer agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


class EvolutionType(Enum):
    TASK_AGENT = "task_agent"
    OPTIMIZER_AGENT = "optimizer_agent"
    MUTUAL = "mutual"


@dataclass
class AgentGenome:
    id: str
    agent_type: EvolutionType
    dna: Dict[str, Any]
    fitness: float = 0.0
    generation: int = 0
    mutations: List[Dict[str, Any]] = field(default_factory=list)


class EscherLoop:
    def __init__(self, config: Dict[str, Any], storage_path: Optional[Path] = None):
        self.config = config
        self.evolution_rate = float(config.get("evolution_rate", 0.1))
        self.mutation_probability = float(config.get("mutation_probability", 0.3))
        self.crossover_enabled = bool(config.get("crossover_enabled", True))

        self.task_population: List[AgentGenome] = []
        self.optimizer_population: List[AgentGenome] = []
        self.generation = 0
        self.performance_history: List[Dict[str, Any]] = []
        self.tournament_pressure = 2.0

        self.storage_path = storage_path
        if self.storage_path:
            self.storage_path.mkdir(parents=True, exist_ok=True)

    async def evolve_mutual(
        self,
        task_evaluation_fn: Callable[[AgentGenome], Any],
        optimizer_evaluation_fn: Callable[[AgentGenome, List[AgentGenome]], Any],
        generations: int = 10,
    ) -> Tuple[Optional[AgentGenome], Optional[AgentGenome]]:
        if not self.task_population:
            self.task_population = await self._initialize_population(EvolutionType.TASK_AGENT)
        if not self.optimizer_population:
            self.optimizer_population = await self._initialize_population(EvolutionType.OPTIMIZER_AGENT)

        best_task: Optional[AgentGenome] = None
        best_optimizer: Optional[AgentGenome] = None

        for gen in range(generations):
            self.generation = gen

            for task_genome in self.task_population:
                task_genome.fitness = float(await task_evaluation_fn(task_genome))

            for optimizer_genome in self.optimizer_population:
                optimizer_genome.fitness = float(await optimizer_evaluation_fn(optimizer_genome, self.task_population))

            best_task = max(self.task_population, key=lambda g: g.fitness)
            best_optimizer = max(self.optimizer_population, key=lambda g: g.fitness)

            generation_report = {
                "generation": gen,
                "best_task_fitness": best_task.fitness,
                "best_optimizer_fitness": best_optimizer.fitness,
                "avg_task_fitness": float(np.mean([g.fitness for g in self.task_population])),
                "avg_optimizer_fitness": float(np.mean([g.fitness for g in self.optimizer_population])),
            }
            self.performance_history.append(generation_report)

            self.task_population = await self._evolve_population(self.task_population, EvolutionType.TASK_AGENT)
            self.optimizer_population = await self._evolve_population(self.optimizer_population, EvolutionType.OPTIMIZER_AGENT)
            await self._apply_optimizer_improvements(best_optimizer)
            self._persist_generation(generation_report)

        return best_task, best_optimizer

    async def _initialize_population(self, agent_type: EvolutionType, size: int = 20) -> List[AgentGenome]:
        return [
            AgentGenome(
                id=f"{agent_type.value}_{i}",
                agent_type=agent_type,
                dna=self._generate_random_dna(agent_type),
                generation=0,
            )
            for i in range(size)
        ]

    def _generate_random_dna(self, agent_type: EvolutionType) -> Dict[str, Any]:
        if agent_type == EvolutionType.TASK_AGENT:
            return {
                "temperature": random.uniform(0.1, 1.0),
                "max_tokens": random.choice([2000, 4000, 8000]),
                "strategy": random.choice(["greedy", "beam_search", "sampling"]),
                "validation_depth": random.randint(1, 5),
                "creativity": random.uniform(0.3, 0.9),
            }
        return {
            "evolution_rate": random.uniform(0.05, 0.3),
            "mutation_strength": random.uniform(0.1, 0.5),
            "selection_pressure": random.uniform(1.5, 3.0),
            "learning_rate": random.uniform(0.001, 0.1),
            "optimization_target": random.choice(["speed", "accuracy", "diversity"]),
        }

    async def _evolve_population(self, population: List[AgentGenome], agent_type: EvolutionType) -> List[AgentGenome]:
        population.sort(key=lambda g: g.fitness, reverse=True)
        elite_count = max(1, len(population) // 5)
        new_population = population[:elite_count]

        while len(new_population) < len(population):
            parent1 = self._tournament_select(population)
            parent2 = self._tournament_select(population)
            child_dna = self._crossover(parent1.dna, parent2.dna) if (self.crossover_enabled and random.random() < 0.7) else dict(parent1.dna)
            if random.random() < self.mutation_probability:
                child_dna = await self._mutate(child_dna, agent_type)

            new_population.append(
                AgentGenome(
                    id=f"{agent_type.value}_{len(new_population)}",
                    agent_type=agent_type,
                    dna=child_dna,
                    generation=self.generation + 1,
                )
            )

        return new_population

    def _tournament_select(self, population: List[AgentGenome], tournament_size: int = 3) -> AgentGenome:
        effective_size = max(2, int(round(tournament_size * self.tournament_pressure / 2)))
        subset = random.sample(population, min(effective_size, len(population)))
        return max(subset, key=lambda g: g.fitness)

    def _crossover(self, dna1: Dict[str, Any], dna2: Dict[str, Any]) -> Dict[str, Any]:
        child: Dict[str, Any] = {}
        for key, value in dna1.items():
            child[key] = random.choice([value, dna2.get(key, value)])
        return child

    async def _mutate(self, dna: Dict[str, Any], agent_type: EvolutionType) -> Dict[str, Any]:
        mutated = dict(dna)
        param = random.choice(list(mutated.keys()))

        if agent_type == EvolutionType.TASK_AGENT:
            if param == "temperature":
                mutated[param] = float(np.clip(mutated[param] + random.gauss(0, 0.1), 0.0, 1.0))
            elif param == "max_tokens":
                options = [2000, 4000, 8000, 16000]
                idx = options.index(mutated[param]) if mutated[param] in options else 1
                mutated[param] = options[int(np.clip(idx + random.choice([-1, 1]), 0, len(options) - 1))]
            elif param == "strategy":
                mutated[param] = random.choice(["greedy", "beam_search", "sampling", "rejection_sampling"])
            elif param == "creativity":
                mutated[param] = float(np.clip(mutated[param] + random.gauss(0, 0.15), 0.0, 1.0))
        else:
            if param == "evolution_rate":
                mutated[param] = float(np.clip(mutated[param] + random.gauss(0, 0.05), 0.0, 0.5))
            elif param == "selection_pressure":
                mutated[param] = float(np.clip(mutated[param] + random.gauss(0, 0.2), 1.0, 5.0))
            elif param == "learning_rate":
                mutated[param] = float(np.clip(mutated[param] + random.gauss(0, 0.01), 0.0001, 0.5))
        return mutated

    async def _apply_optimizer_improvements(self, optimizer: AgentGenome) -> None:
        self.evolution_rate = float(optimizer.dna.get("evolution_rate", self.evolution_rate))
        self.mutation_probability = float(optimizer.dna.get("mutation_strength", self.mutation_probability))
        self.tournament_pressure = float(optimizer.dna.get("selection_pressure", self.tournament_pressure))

    def _persist_generation(self, report: Dict[str, Any]) -> None:
        if not self.storage_path:
            return
        payload = dict(report)
        payload["timestamp"] = datetime.now().isoformat()
        file_path = self.storage_path / f"escher_generation_{self.generation}.json"
        file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
