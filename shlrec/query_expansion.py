"""
Query expansion for generic roles: Use Gemini to expand into skills/competencies.
Helps generic queries like "Consultant" or "Manager" find relevant assessments.
Implements caching to avoid burning free tier quota.
"""

import json
from pathlib import Path
from typing import Optional, Dict
from .phase3_mappings import ROLE_EXPANSIONS


class QueryExpander:
    """Expands generic role names into skills and competencies using Gemini (cached)."""
    
    def __init__(self, cache_path: Optional[str] = None):
        """
        Args:
            cache_path: Path to JSON cache file (optional)
        """
        self.cache_path = Path(cache_path) if cache_path else None
        self._cache: Dict[str, str] = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load expansion cache from disk if exists."""
        if self.cache_path and self.cache_path.exists():
            try:
                self._cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception:
                self._cache = {}
    
    def _save_cache(self):
        """Save expansion cache to disk."""
        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self._cache, ensure_ascii=False), encoding="utf-8")
    
    def expand(self, query_text: str, use_gemini: bool = True) -> str:
        """
        Expand query with skills and competencies.
        
        First tries to use ROLE_EXPANSIONS mapping (no API call needed).
        Falls back to Gemini if enabled and role not in mapping.
        
        Args:
            query_text: Original query (e.g., "hiring a consultant")
            use_gemini: Whether to use Gemini for expansion (requires API key)
        
        Returns:
            Expanded query text including skills/competencies
        """
        # Try rule-based expansion first
        rule_expansion = self._try_rule_expansion(query_text)
        if rule_expansion:
            return rule_expansion
        
        # Fall back to Gemini (if enabled and API key available)
        if use_gemini:
            gemini_expansion = self._try_gemini_expansion(query_text)
            if gemini_expansion:
                return gemini_expansion
        
        # No expansion found, return original
        return query_text
    
    def _try_rule_expansion(self, query_text: str) -> Optional[str]:
        """
        Try to expand query using ROLE_EXPANSIONS mapping.
        Looks for role keywords in query.
        """
        query_lower = query_text.lower()
        
        # Check each role in ROLE_EXPANSIONS
        for role, expansion_data in ROLE_EXPANSIONS.items():
            if role in query_lower:
                skills = expansion_data.get("skills", [])
                # Append skills to original query
                expanded = f"{query_text} {' '.join(skills)}"
                return expanded
        
        return None
    
    def _try_gemini_expansion(self, query_text: str) -> Optional[str]:
        """
        Expand query using Gemini.
        
        Prompt Gemini to extract skills/competencies from the query.
        Uses cache to avoid re-querying same role.
        """
        try:
            from .settings import get_settings
            
            settings = get_settings()
            if not settings.gemini_api_key:
                return None
            
            # Check cache first
            cache_key = query_text.lower().strip()
            if cache_key in self._cache:
                expansion = self._cache[cache_key]
                return f"{query_text} {expansion}"
            
            # Call Gemini
            from google.generativeai import GenerativeModel
            
            model = GenerativeModel(settings.gemini_model)
            prompt = f"""Extract 5-7 key skills, competencies, or job responsibilities from this job query.
Return as a comma-separated list (no bullet points, no explanations).

Query: "{query_text}"

Example response: "leadership, strategic planning, client management, analytical thinking"

Response (comma-separated only):"""
            
            response = model.generate_content(prompt)
            expansion = response.text.strip()
            
            # Cache result
            self._cache[cache_key] = expansion
            self._save_cache()
            
            return f"{query_text} {expansion}"
        
        except Exception as e:
            # Silently fail - query expansion is nice-to-have, not required
            return None


# Legacy function (keep for backward compatibility)
SKILL_SYNONYMS = {
    "python": ["python", "py"],
    "java": ["java", "j2ee"],
    "javascript": ["javascript", "js"],
    "leadership": ["leadership", "leader", "management"],
    "teamwork": ["teamwork", "team", "collaboration"],
}


def expand_query(query: str, max_expansions: int = 1) -> str:
    """Legacy function kept for backward compatibility."""
    return query  # Phase 3 uses QueryExpander class instead


def preprocess_query(query: str) -> str:
    """Preprocess query for better matching."""
    import re
    query = re.sub(r'\s+', ' ', query.strip())
    return query
