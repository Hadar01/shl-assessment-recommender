"""
LLM-based reranking using Gemini for refined candidate scoring.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import json

from .settings import Settings
from .utils import safe_json_loads


RERANK_PROMPT_TEMPLATE = """You are a hiring assessment expert. Given a job requirement and a list of candidate assessments, rank them by relevance.

JOB REQUIREMENT:
{requirement}

CANDIDATE ASSESSMENTS:
{candidates_json}

For each assessment, assign a relevance_score (0.0-1.0) based on how well it matches the job requirement.
Consider: skill match, difficulty level, assessment type (technical vs behavioral).

Return ONLY a valid JSON array like this:
[
  {{"name": "Assessment Name", "relevance_score": 0.95}},
  {{"name": "Assessment Name", "relevance_score": 0.82}},
  ...
]
"""


class GeminiReranker:
    """Uses Gemini API to rerank candidates based on job fit."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._model = None
    
    def _lazy_init(self):
        if self._model is not None:
            return True  # CRITICAL FIX: return True when already initialized
        if not self.settings.gemini_api_key:
            return False
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.settings.gemini_api_key)
            self._model = genai.GenerativeModel(self.settings.gemini_model)
            return True
        except Exception:
            return False
    
    def rerank(
        self, 
        query: str, 
        candidates: List[Dict[str, Any]], 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rerank candidates using Gemini LLM.
        Falls back to input order if Gemini unavailable.
        """
        if not self._lazy_init():
            return candidates[:top_k]
        
        if not candidates:
            return []
        
        try:
            # Format candidates for LLM
            candidates_data = []
            for i, c in enumerate(candidates[:20]):  # Limit to top 20 for cost
                candidates_data.append({
                    "idx": i,
                    "name": c.get("name", ""),
                    "description": c.get("description", "")[:200],  # Truncate
                    "test_type": c.get("test_type", []),
                    "duration": c.get("duration", 0),
                })
            
            candidates_json = json.dumps(candidates_data, indent=2)
            prompt = RERANK_PROMPT_TEMPLATE.format(
                requirement=query[:500],  # Limit query length
                candidates_json=candidates_json
            )
            
            resp = self._model.generate_content(prompt, temperature=0.1)
            text = getattr(resp, "text", "")
            
            scores_data = safe_json_loads(text)
            if not isinstance(scores_data, list):
                return candidates[:top_k]
            
            # Build score map
            score_map = {}
            for item in scores_data:
                if isinstance(item, dict):
                    name = item.get("name", "")
                    score = item.get("relevance_score", 0.0)
                    if name and isinstance(score, (int, float)):
                        score_map[name] = float(score)
            
            # Apply scores and sort
            scored_candidates = []
            for c in candidates:
                name = c.get("name", "")
                original_score = c.get("_score", 0.0)
                llm_score = score_map.get(name, 0.5)
                
                # Blend original and LLM scores (LLM gets 50% weight for tie-breaking)
                blended_score = 0.5 * original_score + 0.5 * llm_score
                c_copy = dict(c)
                c_copy["_score"] = blended_score
                c_copy["_llm_score"] = llm_score
                scored_candidates.append(c_copy)
            
            # Sort by blended score
            scored_candidates.sort(key=lambda x: x.get("_score", 0.0), reverse=True)
            
            return scored_candidates[:top_k]
        
        except Exception:
            # Gracefully fall back to original order
            return candidates[:top_k]
