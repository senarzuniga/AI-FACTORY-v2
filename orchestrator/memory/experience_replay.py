"""Prioritized replay buffer for execution outcomes and feedback."""

from __future__ import annotations

from dataclasses import dataclass
import heapq
import random
from typing import Any, Dict, List


@dataclass(order=True)
class ReplayItem:
    priority: float
    sample: Dict[str, Any]


class ExperienceReplay:
    def __init__(self, capacity: int = 10000, prioritized: bool = True):
        self.capacity = capacity
        self.prioritized = prioritized
        self._items: List[ReplayItem] = []

    def add(self, sample: Dict[str, Any], priority: float = 1.0) -> None:
        item = ReplayItem(priority=max(priority, 1e-6), sample=sample)
        if len(self._items) >= self.capacity:
            heapq.heappushpop(self._items, item)
        else:
            heapq.heappush(self._items, item)

    def sample(self, batch_size: int = 64) -> List[Dict[str, Any]]:
        if not self._items:
            return []

        batch_size = min(batch_size, len(self._items))
        if not self.prioritized:
            return [item.sample for item in random.sample(self._items, batch_size)]

        total = sum(item.priority for item in self._items)
        picks: List[Dict[str, Any]] = []
        for _ in range(batch_size):
            r = random.random() * total
            c = 0.0
            for item in self._items:
                c += item.priority
                if c >= r:
                    picks.append(item.sample)
                    break
        return picks
