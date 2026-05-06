"""I-MCTS with lightweight introspection for repeated-failure avoidance."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import math
import random
from typing import Any, Awaitable, Callable, Dict, List, Optional


@dataclass
class IMCTSNode:
    state: Dict[str, Any]
    parent: Optional["IMCTSNode"] = None
    children: List["IMCTSNode"] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0
    failure_analysis: Optional[Dict[str, Any]] = None
    depth: int = 0
    action_taken: Optional[Dict[str, Any]] = None


class IMCTSEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_depth = int(config.get("max_depth", 5))
        self.exploration_constant = float(config.get("exploration_constant", 1.414))
        self.introspection_budget = int(config.get("introspection_budget", 3))
        self.failure_memory: Dict[str, List[str]] = defaultdict(list)

    async def search(
        self,
        initial_state: Dict[str, Any],
        evaluation_fn: Callable[[Dict[str, Any]], Awaitable[float]],
        max_iterations: int = 100,
    ) -> Dict[str, Any]:
        root = IMCTSNode(state=initial_state, depth=0, visits=1)

        for _ in range(max_iterations):
            node = self._select(root)
            if node.depth < self.max_depth and not node.children:
                node = await self._expand_with_introspection(node, evaluation_fn)
            value = await self._simulate(node.state, evaluation_fn)
            self._backpropagate(node, value)

        if not root.children:
            return {}
        best_child = max(root.children, key=lambda c: (c.value / c.visits) if c.visits else float("-inf"))
        return best_child.action_taken or {}

    def _select(self, node: IMCTSNode) -> IMCTSNode:
        current = node
        while current.children:
            unexplored = [c for c in current.children if c.visits == 0]
            if unexplored:
                return unexplored[0]

            best_score = -float("inf")
            best_child = current.children[0]
            for child in current.children:
                exploitation = child.value / child.visits
                exploration = self.exploration_constant * math.sqrt(max(math.log(max(current.visits, 1)) / child.visits, 0.0))
                introspection_bonus = 0.0
                if child.failure_analysis and child.visits < self.introspection_budget:
                    introspection_bonus = 0.5 * (1 - child.visits / self.introspection_budget)
                score = exploitation + exploration + introspection_bonus
                if score > best_score:
                    best_score = score
                    best_child = child
            current = best_child
        return current

    async def _expand_with_introspection(
        self,
        node: IMCTSNode,
        evaluation_fn: Callable[[Dict[str, Any]], Awaitable[float]],
    ) -> IMCTSNode:
        avoid_actions: List[str] = []
        if node.parent and node.parent.failure_analysis:
            for reason in node.parent.failure_analysis.get("reasons", []):
                analysis = await self._analyze_failure(reason, node.parent.state)
                avoid_actions.extend(analysis.get("actions_to_avoid", []))

        children = await self._generate_children(node.state, evaluation_fn, avoid_actions)
        for child in children:
            child.parent = node
            child.depth = node.depth + 1
        node.children = children

        return random.choice(node.children) if node.children else node

    async def _analyze_failure(self, failure_reason: str, state: Dict[str, Any]) -> Dict[str, Any]:
        _ = state
        reason = failure_reason.lower()
        analysis = {"reasons": [failure_reason], "actions_to_avoid": [], "alternative_strategies": []}
        if "complexity" in reason:
            analysis["actions_to_avoid"].append("generate_high_complexity_solution")
            analysis["alternative_strategies"].append("decompose_into_simpler_tasks")
        elif "security" in reason:
            analysis["actions_to_avoid"].append("skip_security_validation")
            analysis["alternative_strategies"].append("implement_defensive_programming")
        elif "maintainability" in reason:
            analysis["actions_to_avoid"].append("create_tight_coupling")
            analysis["alternative_strategies"].append("use_dependency_injection")
        return analysis

    async def _generate_children(
        self,
        state: Dict[str, Any],
        evaluation_fn: Callable[[Dict[str, Any]], Awaitable[float]],
        avoid_actions: Optional[List[str]] = None,
    ) -> List[IMCTSNode]:
        children: List[IMCTSNode] = []
        for action in self._get_possible_actions(state):
            if avoid_actions and action.get("type") in avoid_actions:
                continue
            new_state = self._apply_action(state, action)
            value = await evaluation_fn(new_state)
            children.append(IMCTSNode(state=new_state, action_taken=action, value=value, visits=1))
        return children

    async def _simulate(self, state: Dict[str, Any], evaluation_fn: Callable[[Dict[str, Any]], Awaitable[float]]) -> float:
        current_state = dict(state)
        depth = int(current_state.get("depth", 0))
        while depth < self.max_depth:
            possible_actions = self._get_possible_actions(current_state)
            if not possible_actions:
                break
            action = random.choice(possible_actions)
            current_state = self._apply_action(current_state, action)
            depth += 1
        return await evaluation_fn(current_state)

    def _backpropagate(self, node: IMCTSNode, value: float) -> None:
        current: Optional[IMCTSNode] = node
        while current is not None:
            current.visits += 1
            current.value += value
            if value < 0.3 and current.parent and current.action_taken:
                if not current.parent.failure_analysis:
                    current.parent.failure_analysis = {"reasons": [], "failed_actions": []}
                current.parent.failure_analysis["reasons"].append(
                    f"Action {current.action_taken.get('type')} resulted in low value {value:.3f}"
                )
                current.parent.failure_analysis["failed_actions"].append(current.action_taken)
            current = current.parent

    def _get_possible_actions(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        _ = state
        return [
            {"type": "refactor_code", "scope": "module"},
            {"type": "add_tests", "coverage": "high"},
            {"type": "optimize_performance", "target": "bottleneck"},
            {"type": "improve_documentation", "format": "api_docs"},
        ]

    def _apply_action(self, state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        new_state = dict(state)
        new_state["last_action"] = action
        new_state["depth"] = int(new_state.get("depth", 0)) + 1

        action_type = action.get("type")
        if action_type == "refactor_code":
            new_state["complexity"] = max(0, float(new_state.get("complexity", 10)) - 2)
            new_state["maintainability"] = float(new_state.get("maintainability", 5)) + 1
        elif action_type == "add_tests":
            new_state["test_coverage"] = min(100, float(new_state.get("test_coverage", 60)) + 20)
            new_state["confidence"] = min(1.0, float(new_state.get("confidence", 0.7)) + 0.1)
        return new_state
