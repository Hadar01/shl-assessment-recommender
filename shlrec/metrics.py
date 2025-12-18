from __future__ import annotations

from typing import List, Sequence, Dict
import numpy as np


def recall_at_k(recommended: Sequence[str], relevant: Sequence[str], k: int) -> float:
    rec_k = list(recommended)[:k]
    rel_set = set(relevant)
    if not rel_set:
        return 0.0
    return len(set(rec_k) & rel_set) / len(rel_set)


def average_precision_at_k(recommended: Sequence[str], relevant: Sequence[str], k: int) -> float:
    rec_k = list(recommended)[:k]
    rel_set = set(relevant)
    if not rel_set:
        return 0.0
    hits = 0
    s = 0.0
    for i, url in enumerate(rec_k, start=1):
        if url in rel_set:
            hits += 1
            s += hits / i
    return s / min(k, len(rel_set))


def mean_metrics(
    query_to_relevant: Dict[str, List[str]],
    query_to_recommended: Dict[str, List[str]],
    k: int = 10,
) -> Dict[str, float]:
    recalls = []
    maps = []
    for q, rel in query_to_relevant.items():
        rec = query_to_recommended.get(q, [])
        recalls.append(recall_at_k(rec, rel, k))
        maps.append(average_precision_at_k(rec, rel, k))
    return {
        f"mean_recall@{k}": float(np.mean(recalls) if recalls else 0.0),
        f"map@{k}": float(np.mean(maps) if maps else 0.0),
    }
