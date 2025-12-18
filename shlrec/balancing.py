from __future__ import annotations

from typing import Any, Dict, List


def pick_balanced(
    candidates: List[Dict[str, Any]],
    k: int,
    kp_weights: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Greedy quota-based balancing on Knowledge&Skills vs Personality&Behavior.

    We treat an assessment as 'K' if its test_type contains 'Knowledge & Skills', and 'P' if contains 'Personality & Behavior'.
    If neither, it can fill any slot.
    """
    k = max(1, min(10, int(k)))

    wK = float(kp_weights.get("K", 0.7))
    wP = float(kp_weights.get("P", 0.3))
    s = max(wK + wP, 1e-6)
    wK, wP = wK / s, wP / s

    quotaK = round(k * wK)
    quotaP = k - quotaK

    selected: List[Dict[str, Any]] = []
    used_urls = set()
    countK = countP = 0

    def tag(item):
        tt = item.get("test_type") or []
        tt = [t.lower() for t in tt]
        hasK = any("knowledge" in t for t in tt)
        hasP = any("personality" in t for t in tt) or any("behavior" in t for t in tt)
        return hasK, hasP

    # fill quotas
    for it in candidates:
        if len(selected) >= k:
            break
        url = it.get("url")
        if not url or url in used_urls:
            continue
        hasK, hasP = tag(it)

        if hasK and countK < quotaK:
            selected.append(it); used_urls.add(url); countK += 1
        elif hasP and countP < quotaP:
            selected.append(it); used_urls.add(url); countP += 1

    # fill remaining
    for it in candidates:
        if len(selected) >= k:
            break
        url = it.get("url")
        if not url or url in used_urls:
            continue
        selected.append(it); used_urls.add(url)

    return selected
