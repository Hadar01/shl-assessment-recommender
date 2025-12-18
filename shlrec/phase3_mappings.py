"""
Phase 3: Corpus enrichment mappings for improved recall on generic and constraint-heavy queries.
Includes: test type synonyms, role expansions, duration keywords, and intent routing rules.
"""

# ============================================================================
# TEST TYPE CODES AND MAPPINGS
# ============================================================================

# Map full test type names to short codes and keywords
TEST_TYPE_MAPPINGS = {
    "Knowledge & Skills": {
        "code": "K",
        "keywords": ["knowledge", "skill", "technical", "expertise", "competency", "professional", "ability"]
    },
    "Personality & Behavior": {
        "code": "P",
        "keywords": ["personality", "behavior", "interpersonal", "collaboration", "teamwork", "leadership", "communication", "culture", "leadership styles", "team types"]
    },
    "Ability & Aptitude": {
        "code": "A",
        "keywords": ["ability", "aptitude", "reasoning", "cognitive", "analytical", "numerical", "verbal", "logical", "problem-solving"]
    },
    "Biodata & Situational Judgement": {
        "code": "SJ",
        "keywords": ["situational", "judgment", "judgement", "biodata", "scenario", "decision-making", "judgment"]
    },
    "Competencies": {
        "code": "C",
        "keywords": ["competency", "competencies", "skill", "capability"]
    }
}

# ============================================================================
# ROLE EXPANSION SYNONYMS (for generic role names)
# ============================================================================

ROLE_EXPANSIONS = {
    "consultant": {
        "skills": ["client-facing", "advisory", "problem-solving", "stakeholder management", "delivery", "analytical", "decision-making", "collaboration"],
        "test_types": ["P", "A", "K"]  # Personality, Ability, Knowledge
    },
    "manager": {
        "skills": ["leadership", "team management", "strategic thinking", "decision-making", "communication", "analytical", "numerical", "interpersonal"],
        "test_types": ["P", "A"]  # Personality & Leadership, Ability
    },
    "coo": {
        "skills": ["executive", "strategic", "leadership", "organizational", "cultural fit", "decision-making", "personality", "behavior", "collaboration"],
        "test_types": ["P", "A", "K"]  # Focus on personality & behavior for culture fit
    },
    "senior admin": {
        "skills": ["administrative", "data entry", "clerical", "detail-oriented", "attention to detail", "numerical", "accuracy"],
        "test_types": ["K", "A"]  # Knowledge & Aptitude
    },
    "admin": {
        "skills": ["administrative", "clerical", "data entry", "detail-oriented", "attention to detail", "numerical", "accuracy", "banking", "financial"],
        "test_types": ["K", "A"]  # Knowledge & Aptitude
    },
    "qa engineer": {
        "skills": ["quality assurance", "testing", "selenium", "automation", "sql", "technical", "manual testing", "functional testing"],
        "test_types": ["K", "A"]  # Knowledge & Ability
    },
    "content writer": {
        "skills": ["writing", "english", "communication", "seo", "content", "verbal", "written english"],
        "test_types": ["K", "C"]  # Knowledge, Competencies
    },
    "marketing manager": {
        "skills": ["marketing", "leadership", "strategic", "communication", "digital", "advertising", "team management", "decision-making"],
        "test_types": ["P", "A", "K"]  # Personality, Ability, Knowledge
    }
}

# ============================================================================
# DURATION KEYWORDS AND NORMALIZATION
# ============================================================================

DURATION_KEYWORDS = {
    "30": ["30", "half hour", "30 min", "30-minute", "30-40", "30-45"],
    "40": ["40", "40 min", "40-minute", "30-40", "35-45"],
    "60": ["60", "1 hour", "one hour", "hour", "hourly", "60 min", "60-minute"],
    "90": ["90", "90 min", "90-minute", "hour and half", "1.5 hour"],
    "120": ["120", "2 hour", "two hour", "2-hour", "120 min"]
}

# ============================================================================
# TEST TYPE INTENT ROUTER
# ============================================================================

INTENT_ROUTER_RULES = {
    # If query contains these keywords, ensure these test types are prioritized
    "personality_keywords": ["personality", "behavior", "collaborate", "stakeholders", "cultural", "culture fit", "team", "interpersonal", "leadership", "management"],
    "personality_test_types": ["P"],  # Personality & Behavior
    
    "cognitive_keywords": ["cognitive", "reasoning", "analytical", "problem", "logic", "numerical", "verbal", "aptitude", "ability"],
    "cognitive_test_types": ["A"],  # Ability & Aptitude
    
    "technical_keywords": ["technical", "programming", "developer", "engineer", "sql", "java", "javascript", "python", "automation", "testing"],
    "technical_test_types": ["K", "A"],  # Knowledge & Ability
    
    "admin_keywords": ["admin", "clerical", "data entry", "attention to detail", "banking", "financial", "entry level"],
    "admin_test_types": ["K", "A"],  # Knowledge & Aptitude (clerical focus)
}

# ============================================================================
# DURATION CONSTRAINT SOFTENING
# ============================================================================

# When a query specifies a duration, how strictly should we filter?
# "soft" = allow +/- 15 minutes
# "medium" = allow +/- 10 minutes
# "strict" = exact match or within 5 minutes

DURATION_CONSTRAINT_LEVEL = "soft"  # Can be overridden per query

def get_duration_tolerance(level: str = DURATION_CONSTRAINT_LEVEL) -> int:
    """Returns minute tolerance for duration constraint."""
    tolerances = {
        "strict": 5,
        "medium": 10,
        "soft": 15
    }
    return tolerances.get(level, 15)

# ============================================================================
# SCORING BOOST FOR DURATION PROXIMITY
# ============================================================================

def calculate_duration_score_boost(query_duration: int, item_duration: int, max_boost: float = 0.2) -> float:
    """
    Calculate a score boost for duration proximity.
    
    Returns boost between 0 and max_boost based on how close item duration is to query duration.
    Closer match = higher boost.
    """
    if query_duration is None or item_duration is None:
        return 0.0
    
    diff = abs(query_duration - item_duration)
    
    # Linear penalty: no difference = max_boost, 30 min diff = 0 boost
    if diff <= 30:
        return max_boost * (1 - diff / 30)
    else:
        return 0.0
