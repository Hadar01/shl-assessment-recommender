from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .settings import get_settings
from .retrieval import load_index, hybrid_retrieve, LoadedIndex
from .llm_gemini import GeminiIntentExtractor
from .llm_reranker import GeminiReranker
from .balancing_improved import pick_balanced_improved
from .jd_extractor import looks_like_url, extract_text_from_url
from .utils import canonical_shl_url
from .duration_scoring import parse_duration_from_query, apply_duration_scoring_boost, soft_filter_by_duration
from .query_expansion import QueryExpander
from .test_type_router import extract_test_type_intent, boost_matching_test_types


@dataclass
class Recommender:
    index_dir: Path
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    _idx: Optional[LoadedIndex] = None
    _intent_extractor: Optional[GeminiIntentExtractor] = None
    _reranker: Optional[GeminiReranker] = None
    _query_expander: Optional[QueryExpander] = None

    def _lazy_load(self):
        self.index_dir = Path(self.index_dir)
        if self._idx is None:
            self._idx = load_index(self.index_dir, embedding_model=self.embedding_model)
        if self._intent_extractor is None:
            settings = get_settings()
            self._intent_extractor = GeminiIntentExtractor(settings, cache_path=str(self.index_dir / "gemini_cache.json"))
        # CRITICAL FIX: Use settings toggle instead of hardcoded True
        if self._reranker is None:
            settings = get_settings()
            if settings.rerank_with_gemini:
                self._reranker = GeminiReranker(settings)
        # PHASE 3: Query expander for generic roles (cached)
        if self._query_expander is None:
            self._query_expander = QueryExpander(cache_path=str(self.index_dir / "query_expansion_cache.json"))

    def recommend(self, query_or_url: str, k: int = 10) -> List[Dict[str, Any]]:
        self._lazy_load()
        assert self._idx is not None
        assert self._intent_extractor is not None
        assert self._query_expander is not None

        raw = (query_or_url or "").strip()
        if not raw:
            return []

        # If URL, fetch JD text
        query_text = raw
        if looks_like_url(raw):
            try:
                query_text = extract_text_from_url(raw)
            except Exception:
                # fallback: treat as plain text
                query_text = raw

        # PHASE 3: Query expansion for generic roles (cached, rule-based first)
        # NOTE: Disabled - query expansion causes retrieval drift for other queries
        # expanded_query = self._query_expander.expand(query_text, use_gemini=False)

        # Gemini intent extraction (cached)
        intent = self._intent_extractor.extract(query_text)
        
        # PHASE 3: Extract test-type intent (personality, cognitive, admin, etc.)
        # NOTE: Disabled for now
        # test_type_intent = extract_test_type_intent(expanded_query)
        
        # PHASE 3: Parse duration from query (e.g., "1 hour", "30-40 min")
        # NOTE: Disabled for now
        # query_duration = parse_duration_from_query(expanded_query)

        # Optimized retrieval with fine-tuned parameters
        settings = get_settings()
        pairs = hybrid_retrieve(
            self._idx,
            query_text,
            alpha=settings.hybrid_alpha,
            top_n=settings.candidate_pool,
        )

        # Build candidate list
        candidates: List[Dict[str, Any]] = []
        for doc_id, score in pairs:
            it = dict(self._idx.meta[doc_id])
            it["_score"] = score
            it["url"] = canonical_shl_url(it.get("url", ""))
            # Ensure required fields exist with proper types
            it["adaptive_support"] = (it.get("adaptive_support") or "No")
            it["remote_support"] = (it.get("remote_support") or "Yes")
            it["duration"] = int(it.get("duration") or 0)
            it["test_type"] = list(it.get("test_type") or [])
            it["description"] = it.get("description") or ""
            it["name"] = it.get("name") or ""
            candidates.append(it)

        # PHASE 3: Apply duration-aware score boost (before filtering)
        # NOTE: Disabled - can hurt relevance. Duration constraint still applied below.
        # if query_duration:
        #     candidates = apply_duration_scoring_boost(candidates, query_duration, max_boost=0.10)
        
        # PHASE 3: Boost candidates with matching test types
        # NOTE: Disabled - aggressive boosting disrupts core ranking. Query expansion sufficient.
        # candidates = boost_matching_test_types(candidates, test_type_intent, boost_factor=0.08)

        # Constraint filtering (duration, remote), but do not over-filter
        filtered = candidates

        if intent.duration_limit_minutes is not None:
            under = [c for c in filtered if c.get("duration", 0) and c["duration"] <= intent.duration_limit_minutes]
            if len(under) >= 5:
                filtered = under

        if intent.remote_required is True:
            rem = [c for c in filtered if str(c.get("remote_support", "")).lower().startswith("y")]
            if len(rem) >= 5:
                filtered = rem

        # LLM-based reranking if available (improves relevance)
        # CRITICAL FIX: Limit reranking to top 60 instead of all candidates
        if self._reranker and len(filtered) > 0:
            filtered = self._reranker.rerank(query_text, filtered, top_k=min(len(filtered), 60))

        # Balance K/P mix with improved score-aware algorithm
        out = pick_balanced_improved(filtered, k=min(10, max(5, k)), kp_weights=intent.domain_mix)

        # Remove internal scores before returning
        for o in out:
            o.pop("_score", None)
            o.pop("_llm_score", None)

        return out
