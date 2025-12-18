"""
Corpus enrichment: Build enhanced document text with test types, durations, synonyms.
Used by indexer.py to create richer indexed content for better retrieval.
"""

from typing import Dict, Any, List
from .phase3_mappings import TEST_TYPE_MAPPINGS, DURATION_KEYWORDS


def build_enriched_corpus_text(item: Dict[str, Any]) -> str:
    """
    Build enriched corpus text for a single assessment item.
    
    Includes:
    - Name and description
    - Test type codes (K, P, A, etc.) and full names
    - Duration tokens (e.g., "DurationMinutes: 60")
    - Job level if available
    - Remote/adaptive support
    - Test type keywords
    
    Args:
        item: Assessment item from catalog with keys: name, description, test_type, duration, etc.
    
    Returns:
        Enriched text string optimized for BM25 + semantic search
    """
    parts = []
    
    # ========== BASE FIELDS ==========
    name = item.get("name", "").strip()
    description = item.get("description", "").strip()
    
    if name:
        parts.append(name)
    if description:
        parts.append(description)
    
    # ========== TEST TYPE CODES AND NAMES ==========
    test_types = item.get("test_type", []) or []
    test_type_codes = []
    
    for tt in test_types:
        if tt in TEST_TYPE_MAPPINGS:
            mapping = TEST_TYPE_MAPPINGS[tt]
            test_type_codes.append(mapping["code"])
    
    # Add test type codes (e.g., "TestTypeCodes: K P A")
    if test_type_codes:
        parts.append(f"TestTypeCodes: {' '.join(test_type_codes)}")
    
    # Add test type full names (e.g., "TestTypeNames: Knowledge Personality Ability")
    if test_types:
        parts.append(f"TestTypeNames: {' '.join(test_types)}")
    
    # REMOVED: TestTypeKeywords - adding too many generic words dilutes BM25 signal
    # Keywords are useful for semantic search, but hurt exact/keyword matching
    
    # ========== DURATION TOKENS ==========
    duration = item.get("duration")
    if duration:
        duration = int(duration)
        # Add duration number
        parts.append(f"DurationMinutes: {duration}")
        
        # Add duration keywords (e.g., "60 minutes" → also index as "hour", "1-hour")
        duration_keywords = _get_duration_keywords(duration)
        if duration_keywords:
            parts.append(f"DurationKeywords: {' '.join(duration_keywords)}")
    
    # ========== SUPPORT FLAGS ==========
    remote = item.get("remote_support", "").strip()
    if remote:
        parts.append(f"Remote: {remote}")
    
    adaptive = item.get("adaptive_support", "").strip()
    if adaptive:
        parts.append(f"Adaptive: {adaptive}")
    
    # ========== JOB LEVELS (if scraped, not in current catalog but future-proof) ==========
    job_level = item.get("job_level", "").strip()
    if job_level:
        parts.append(f"JobLevel: {job_level}")
    
    return " . ".join(parts)


def _get_duration_keywords(duration_minutes: int) -> List[str]:
    """
    Get duration synonym keywords for a given duration in minutes.
    
    Maps exact durations to alternative phrases (e.g., 60 → "1 hour", "hourly")
    This helps queries like "1 hour test" find "60 minutes" assessments.
    
    Args:
        duration_minutes: Duration in minutes (e.g., 60, 30, 45)
    
    Returns:
        List of synonymous keywords to add to corpus
    """
    keywords = []
    
    # Check exact match
    for duration_key, keyword_list in DURATION_KEYWORDS.items():
        if int(duration_key) == duration_minutes:
            keywords.extend(keyword_list)
    
    # Check close range matches (within 5 minutes)
    for duration_key, keyword_list in DURATION_KEYWORDS.items():
        key_int = int(duration_key)
        if abs(key_int - duration_minutes) <= 5:
            keywords.extend(keyword_list)
    
    # Remove duplicates and return
    return list(set(keywords))
