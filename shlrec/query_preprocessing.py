"""
Advanced query preprocessing for improved retrieval.
Includes stop word removal, stemming, and intelligent term weighting.
"""
from __future__ import annotations

import re
from typing import List, Tuple

# Common English stop words to remove
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "can", "in", "on", "at", "by", "for", "of", "to", "from", "up", "about", "out",
    "if", "as", "with", "it", "this", "that", "these", "those", "i", "you", "he", "she", "we", "they",
    "what", "which", "who", "whom", "whose", "where", "when", "why", "how",
}

# High-value technical keywords that shouldn't be removed
TECH_KEYWORDS = {
    "sql", "java", "python", "javascript", "cpp", "csharp", "ruby", "golang", "rust", "kotlin",
    "react", "angular", "vue", "node", "express", "django", "flask", "spring", "hibernate",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "devops", "ci/cd",
    "api", "rest", "graphql", "microservices", "cloud", "serverless", "lambda",
    "agile", "scrum", "kanban", "jira", "confluence",
}

# Skill synonyms and variations
SKILL_VARIATIONS = {
    "communication": ["communicat", "verbal", "written", "presentation", "speaking"],
    "leadership": ["leadership", "leader", "lead", "management", "manage", "supervise"],
    "teamwork": ["teamwork", "team", "collaboration", "collaborat", "cooperat", "cooperative"],
    "problem solving": ["problem", "solving", "analytical", "analysis", "critical", "thinking"],
    "project management": ["project", "management", "pmp", "agile", "scrum", "kanban"],
    "technical": ["technical", "technical", "coding", "programming", "development"],
}


def simple_stem(word: str) -> str:
    """Simple stemming by removing common suffixes."""
    word = word.lower()
    # Remove common suffixes
    for suffix in ["tion", "ment", "ing", "ed", "er", "est", "ly", "ness"]:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word


def normalize_query(query: str) -> str:
    """Normalize query: lowercase, remove extra spaces."""
    query = query.lower()
    query = re.sub(r'\s+', ' ', query)
    return query.strip()


def extract_keywords(query: str) -> List[str]:
    """
    Extract meaningful keywords from query.
    Removes stop words but keeps technical terms.
    """
    query = normalize_query(query)
    
    # Split by non-alphanumeric chars
    tokens = re.findall(r'\b\w+\b', query)
    
    keywords = []
    for token in tokens:
        token_lower = token.lower()
        
        # Keep tech keywords even if they might be stop words
        if token_lower in TECH_KEYWORDS:
            keywords.append(token_lower)
        # Remove common stop words
        elif token_lower not in STOP_WORDS:
            keywords.append(token_lower)
    
    return keywords


def extract_phrases(query: str) -> List[str]:
    """Extract 2-3 word phrases for better semantic matching."""
    query = normalize_query(query)
    tokens = re.findall(r'\b\w+\b', query)
    
    phrases = []
    # 2-word phrases
    for i in range(len(tokens) - 1):
        phrase = f"{tokens[i]} {tokens[i+1]}"
        if not any(sw in phrase.lower() for sw in ["the", "a", "is", "and", "or"]):
            phrases.append(phrase.lower())
    
    # 3-word phrases
    for i in range(len(tokens) - 2):
        phrase = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
        if len(phrase.split()) >= 2:
            phrases.append(phrase.lower())
    
    return phrases[:3]  # Limit to top 3


def detect_query_complexity(query: str) -> float:
    """
    Detect query complexity to adjust weighting.
    Returns value 0.0-1.0 where:
    - 0.0 = simple keyword query (prefer BM25)
    - 1.0 = complex narrative query (prefer semantic)
    """
    query_lower = query.lower()
    length = len(query.split())
    
    complexity_score = 0.0
    
    # Long queries are more semantic/narrative
    if length > 20:
        complexity_score += 0.3
    elif length > 10:
        complexity_score += 0.15
    
    # Queries with soft skills are more semantic
    soft_skill_words = ["communication", "teamwork", "leadership", "collaboration", 
                       "culture", "fit", "mindset", "behavior", "personality"]
    if any(word in query_lower for word in soft_skill_words):
        complexity_score += 0.3
    
    # Queries with role descriptions are more semantic
    role_keywords = ["developer", "engineer", "manager", "analyst", "designer", "architect"]
    if sum(1 for role in role_keywords if role in query_lower) > 1:
        complexity_score += 0.2
    
    return min(complexity_score, 1.0)


def preprocess_query_advanced(query: str) -> Tuple[str, List[str], List[str], float]:
    """
    Advanced query preprocessing.
    Returns: (normalized_query, keywords, phrases, complexity)
    """
    normalized = normalize_query(query)
    keywords = extract_keywords(query)
    phrases = extract_phrases(query)
    complexity = detect_query_complexity(query)
    
    # Reconstruct boosted query with keywords and important phrases
    boosted_terms = []
    if phrases:
        boosted_terms.extend(phrases)
    boosted_terms.extend(keywords)
    
    boosted_query = normalized
    if boosted_terms:
        boosted_query = normalized + " " + " ".join(boosted_terms[:5])
    
    return boosted_query, keywords, phrases, complexity


def get_dynamic_alpha(complexity: float, base_alpha: float = 0.40) -> float:
    """
    Get dynamic alpha based on query complexity.
    - Simple queries: higher BM25 weight (more alpha)
    - Complex queries: higher semantic weight (less alpha)
    """
    # Range: base_alpha±0.15
    min_alpha = max(0.1, base_alpha - 0.15)
    max_alpha = min(0.9, base_alpha + 0.15)
    
    # Invert complexity (low complexity = high BM25)
    adjusted_alpha = base_alpha + (0.5 - complexity) * 0.15
    
    return max(min_alpha, min(max_alpha, adjusted_alpha))
