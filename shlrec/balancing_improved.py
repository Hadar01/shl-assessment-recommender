"""
Improved balancing algorithm that preserves ranking quality while maintaining K/P mix.
Uses score-aware selection instead of greedy quota filling.
"""
from __future__ import annotations

from typing import Any, Dict, List


def pick_balanced_improved(
    candidates: List[Dict[str, Any]],
    k: int,
    kp_weights: Dict[str, float],
) -> List[Dict[str, Any]]:
    """
    Score-aware balancing on Knowledge&Skills vs Personality&Behavior.
    
    This improves upon the greedy approach by:
    1. Sorting candidates by score within each category
    2. Interleaving top-K candidates to maintain balance
    3. Only deviating from score order when necessary to meet quotas
    """
    k = max(1, min(10, int(k)))

    wK = float(kp_weights.get("K", 0.7))
    wP = float(kp_weights.get("P", 0.3))
    s = max(wK + wP, 1e-6)
    wK, wP = wK / s, wP / s

    quotaK = round(k * wK)
    quotaP = k - quotaK

    def tag(item):
        tt = item.get("test_type") or []
        tt = [t.lower() for t in tt]
        hasK = any("knowledge" in t for t in tt)
        hasP = any("personality" in t for t in tt) or any("behavior" in t for t in tt)
        return hasK, hasP

    # Separate candidates by type, preserving score order
    k_candidates = []
    p_candidates = []
    neutral_candidates = []

    for it in candidates:
        url = it.get("url")
        if not url:
            continue
        hasK, hasP = tag(it)
        
        if hasK and hasP:
            neutral_candidates.append(it)
        elif hasK:
            k_candidates.append(it)
        elif hasP:
            p_candidates.append(it)
        else:
            neutral_candidates.append(it)

    # Sort each group by score (descending)
    k_candidates.sort(key=lambda x: x.get("_score", 0.0), reverse=True)
    p_candidates.sort(key=lambda x: x.get("_score", 0.0), reverse=True)
    neutral_candidates.sort(key=lambda x: x.get("_score", 0.0), reverse=True)

    selected: List[Dict[str, Any]] = []
    used_urls = set()
    countK = countP = 0

    # First pass: Fill quotas with best candidates from each category
    for it in k_candidates:
        if countK >= quotaK:
            break
        url = it.get("url")
        if url not in used_urls:
            selected.append(it)
            used_urls.add(url)
            countK += 1

    for it in p_candidates:
        if countP >= quotaP:
            break
        url = it.get("url")
        if url not in used_urls:
            selected.append(it)
            used_urls.add(url)
            countP += 1

    # Second pass: Fill remaining slots with neutral candidates
    for it in neutral_candidates:
        if len(selected) >= k:
            break
        url = it.get("url")
        if url not in used_urls:
            # Try to balance K/P still
            if countK < quotaK:
                selected.append(it)
                used_urls.add(url)
                countK += 1
            elif countP < quotaP:
                selected.append(it)
                used_urls.add(url)
                countP += 1

    # Third pass: If we still need items, take from any remaining
    for it in candidates:
        if len(selected) >= k:
            break
        url = it.get("url")
        if url not in used_urls:
            selected.append(it)
            used_urls.add(url)

    return selected
