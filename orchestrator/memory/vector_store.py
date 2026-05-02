"""Vector store abstraction with optional FAISS backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import faiss
except ImportError:  # pragma: no cover
    faiss = None


@dataclass
class VectorRecord:
    key: str
    vector: np.ndarray
    payload: Dict[str, Any]


class VectorStore:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.records: List[VectorRecord] = []
        self.index = faiss.IndexFlatIP(dimension) if faiss else None

    def add(self, key: str, vector: List[float], payload: Optional[Dict[str, Any]] = None) -> None:
        arr = np.array(vector, dtype=np.float32).reshape(1, -1)
        if arr.shape[1] != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {arr.shape[1]}")

        record = VectorRecord(key=key, vector=arr[0], payload=payload or {})
        self.records.append(record)
        if self.index is not None:
            faiss.normalize_L2(arr)
            self.index.add(arr)

    def query(self, vector: List[float], top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        if not self.records:
            return []

        arr = np.array(vector, dtype=np.float32).reshape(1, -1)
        if self.index is None:
            # Fallback cosine-like scoring when FAISS is unavailable.
            norm = np.linalg.norm(arr[0]) + 1e-9
            scores = []
            for rec in self.records:
                sim = float(np.dot(arr[0], rec.vector) / (norm * (np.linalg.norm(rec.vector) + 1e-9)))
                scores.append((rec.key, sim, rec.payload))
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:top_k]

        faiss.normalize_L2(arr)
        distances, indices = self.index.search(arr, min(top_k, len(self.records)))
        output: List[Tuple[str, float, Dict[str, Any]]] = []
        for idx, score in zip(indices[0], distances[0]):
            rec = self.records[int(idx)]
            output.append((rec.key, float(score), rec.payload))
        return output
