"""
Test-type intent router: Rule-based filtering to ensure correct test types.
For generic queries, ensures we prioritize relevant test type categories.
Helps fix queries like "Consultant" where personality tests are crucial.
"""

from typing import List, Dict, Any, Optional
from .phase3_mappings import INTENT_ROUTER_RULES


def extract_test_type_intent(query_text: str) -> Dict[str, Any]:
    """
    Extract test type intent from query.
    
    Returns a dict with:
    - required_test_types: List of test type codes that MUST be included
    - preferred_test_types: List of test types to prioritize
    - exclude_test_types: List of test types to avoid (optional)
    
    Args:
        query_text: Raw query text
    
    Returns:
        Intent dict with test type preferences
    """
    query_lower = query_text.lower()
    intent = {
        "required_test_types": [],
        "preferred_test_types": [],
        "exclude_test_types": []
    }
    
    # Check personality keywords
    for keyword in INTENT_ROUTER_RULES.get("personality_keywords", []):
        if keyword in query_lower:
            intent["preferred_test_types"].extend(INTENT_ROUTER_RULES.get("personality_test_types", []))
            break
    
    # Check cognitive keywords
    for keyword in INTENT_ROUTER_RULES.get("cognitive_keywords", []):
        if keyword in query_lower:
            intent["preferred_test_types"].extend(INTENT_ROUTER_RULES.get("cognitive_test_types", []))
            break
    
    # Check technical keywords
    for keyword in INTENT_ROUTER_RULES.get("technical_keywords", []):
        if keyword in query_lower:
            intent["preferred_test_types"].extend(INTENT_ROUTER_RULES.get("technical_test_types", []))
            break
    
    # Check admin keywords
    for keyword in INTENT_ROUTER_RULES.get("admin_keywords", []):
        if keyword in query_lower:
            intent["preferred_test_types"].extend(INTENT_ROUTER_RULES.get("admin_test_types", []))
            break
    
    # Remove duplicates
    intent["preferred_test_types"] = list(set(intent["preferred_test_types"]))
    
    return intent


def boost_matching_test_types(
    candidates: List[Dict[str, Any]],
    query_intent: Dict[str, Any],
    boost_factor: float = 0.15
) -> List[Dict[str, Any]]:
    """
    Boost candidates that match the test type intent.
    
    If query has personality keywords, boost personality tests.
    If query has technical keywords, boost knowledge tests.
    
    Args:
        candidates: List of candidate assessments with _score
        query_intent: Intent dict from extract_test_type_intent
        boost_factor: Score boost multiplier (default 0.15 = 15%)
    
    Returns:
        Candidates with boosted scores for matching test types
    """
    preferred_types = query_intent.get("preferred_test_types", [])
    if not preferred_types or not candidates:
        return candidates
    
    boosted = []
    for candidate in candidates:
        test_type_codes = candidate.get("test_type", [])
        
        # Check if candidate has any preferred test type codes
        has_preferred = any(
            code in test_type_codes for code in preferred_types
        )
        
        if has_preferred:
            # Boost score
            original_score = candidate.get("_score", 0.0)
            candidate["_score"] = original_score + (original_score * boost_factor)
            candidate["_test_type_boost"] = True
        else:
            candidate["_test_type_boost"] = False
        
        boosted.append(candidate)
    
    # Re-sort by boosted scores
    return sorted(boosted, key=lambda x: x.get("_score", 0), reverse=True)


def ensure_test_type_coverage(
    candidates: List[Dict[str, Any]],
    query_intent: Dict[str, Any],
    k: int = 10
) -> List[Dict[str, Any]]:
    """
    Ensure final results cover the required test types.
    
    If query specifies "I need personality tests", make sure final results
    include at least some personality tests (codes 'P').
    
    Args:
        candidates: Sorted list of candidates (pre-filtered by score)
        query_intent: Intent dict from extract_test_type_intent
        k: Number of results to return
    
    Returns:
        Final results ensuring test type coverage
    """
    required_types = query_intent.get("required_test_types", [])
    if not required_types or not candidates:
        return candidates[:k]
    
    result = []
    covered_types = set()
    
    # First pass: include items covering required types
    for candidate in candidates:
        test_type_codes = candidate.get("test_type", [])
        
        # Check if this candidate has any uncovered required types
        has_uncovered = any(
            code in test_type_codes and code not in covered_types
            for code in required_types
        )
        
        if has_uncovered:
            result.append(candidate)
            covered_types.update(test_type_codes)
            if len(result) >= k:
                return result
    
    # Second pass: fill remaining slots with top-scoring candidates
    for candidate in candidates:
        if len(result) >= k:
            break
        if candidate not in result:
            result.append(candidate)
    
    return result
