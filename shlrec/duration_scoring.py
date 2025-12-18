"""
Duration-aware re-ranking: Apply score boost based on duration proximity.
Helps fix queries with strict duration constraints (e.g., "30-40 min", "1 hour").
"""

from typing import List, Dict, Any, Optional
from .phase3_mappings import calculate_duration_score_boost, get_duration_tolerance


def parse_duration_from_query(query_text: str) -> Optional[int]:
    """
    Extract duration target from query text.
    
    Looks for patterns like:
    - "1 hour", "1-hour", "60 min", "60 minutes"
    - "30-40 min", "30-40 minutes" → uses midpoint 35
    - "2 hour", "120 min"
    
    Args:
        query_text: Raw query text
    
    Returns:
        Duration in minutes, or None if not found
    """
    import re
    
    query_lower = query_text.lower()
    
    # Pattern 1: Range (e.g., "30-40 min", "30-45 minutes")
    range_match = re.search(r'(\d+)\s*[-–]\s*(\d+)\s*(?:min|minute)', query_lower)
    if range_match:
        min_dur = int(range_match.group(1))
        max_dur = int(range_match.group(2))
        return (min_dur + max_dur) // 2  # Return midpoint
    
    # Pattern 2: "X hour(s)" 
    hour_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:-?\s*hour|hr|hrs)', query_lower)
    if hour_match:
        hours = float(hour_match.group(1))
        return int(hours * 60)
    
    # Pattern 3: "X min(utes)"
    min_match = re.search(r'(\d+)\s*(?:min|minute)', query_lower)
    if min_match:
        return int(min_match.group(1))
    
    return None


def apply_duration_scoring_boost(
    candidates: List[Dict[str, Any]],
    query_duration: Optional[int],
    max_boost: float = 0.2
) -> List[Dict[str, Any]]:
    """
    Apply score boost based on duration proximity.
    
    Boosts candidates whose duration is close to query duration.
    Soft constraint: still includes items with different durations, but demotes them.
    
    Args:
        candidates: List of candidate assessments with _score field
        query_duration: Target duration in minutes (e.g., 60, 35, 90)
        max_boost: Maximum boost to apply (default 0.2 = 20% of original score)
    
    Returns:
        Same candidates with _score updated to include duration boost
    """
    if query_duration is None or not candidates:
        return candidates
    
    boosted = []
    for candidate in candidates:
        item_duration = candidate.get("duration")
        
        if item_duration:
            boost = calculate_duration_score_boost(query_duration, item_duration, max_boost)
            # Apply boost: new_score = old_score + (old_score * boost)
            original_score = candidate.get("_score", 0.0)
            candidate["_score"] = original_score + (original_score * boost)
            candidate["_duration_boost"] = boost  # Track boost for debugging
        else:
            candidate["_duration_boost"] = 0.0
        
        boosted.append(candidate)
    
    # Sort by new score (descending)
    return sorted(boosted, key=lambda x: x.get("_score", 0), reverse=True)


def soft_filter_by_duration(
    candidates: List[Dict[str, Any]],
    query_duration: Optional[int],
    min_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Soft filter: only apply duration constraint if we have enough results.
    
    This prevents zero-result scenarios by:
    1. First try exact matches (within tolerance)
    2. If < min_results, relax and allow all candidates
    
    Args:
        candidates: List of candidate assessments
        query_duration: Target duration in minutes
        min_results: Minimum results to require before relaxing
    
    Returns:
        Filtered candidates (or all candidates if not enough matches)
    """
    if query_duration is None or not candidates:
        return candidates
    
    tolerance = get_duration_tolerance()
    
    # Find candidates within tolerance
    matching = [
        c for c in candidates
        if c.get("duration") and abs(c["duration"] - query_duration) <= tolerance
    ]
    
    # If we have enough, return filtered. Otherwise return all.
    if len(matching) >= min_results:
        return matching
    else:
        return candidates
