# Phase 3: Corpus Enrichment & Query Optimization - Summary

## What Was Implemented

Successfully created 4 new Phase 3 modules:

1. **`shlrec/phase3_mappings.py`** (152 lines)
   - Test type code mappings (K, P, A, SJ, C)
   - Role expansion synonyms (consultant, manager, coo, admin, etc.)
   - Duration keywords (30, 40, 60, 90, 120 minutes)
   - Intent routing rules
   - Duration scoring formula

2. **`shlrec/corpus_enrichment.py`** (121 lines)
   - Enhanced corpus text builder
   - Test type code injection
   - Duration tokenization
   - Keyword extraction

3. **`shlrec/duration_scoring.py`** (110 lines)
   - Duration parsing from natural language
   - Duration-aware re-ranking with score boosting
   - Soft filtering logic

4. **`shlrec/query_expansion.py`** (157 lines)
   - QueryExpander class with caching
   - Rule-based role expansion (consultant → client-facing, problem-solving, etc.)
   - Gemini API fallback for custom role expansion
   - Cache persistence to JSON

5. **`shlrec/test_type_router.py`** (170 lines)
   - Test-type intent extraction
   - Boost matching test types (P, A, K)
   - Ensure test-type coverage in final results

6. **Updated `shlrec/recommender.py`**
   - Added Phase 3 imports and QueryExpander
   - Integrated query expansion, duration parsing, test-type routing

## Performance Testing Results

| Configuration | Recall@10 | MAP@10 | Notes |
|---------------|-----------|--------|-------|
| **Baseline** | 23.78% | 16.74% | Original: HYBRID_ALPHA=0.39 |
| With corpus enrichment | 14.67% | 11.07% | **-37% degradation** |
| Simplified enrichment (no keywords) | 14.67% | 11.07% | Still degraded |
| Original index + query expansion | 21.78% | 15.10% | **-8% degradation** |
| Original index + no enhancements | 23.78% | 16.74% | ✅ Baseline restored |

## Key Learnings

### Why Phase 3 Features Hurt Performance

1. **Corpus Enrichment Issues**
   - Adding 80+ keywords per document via "TestTypeKeywords" field
   - BM25 vocabulary explosion dilutes term importance
   - Keywords are too generic (e.g., "skill", "knowledge", "ability" appear in many docs)
   - Result: Reduced precision in keyword matching

2. **Query Expansion Issues**
   - Expanding "Consultant" → "... client-facing advisory problem-solving ..."
   - Adds 8-10 tokens that don't all match indexed content
   - Increases query drift for subsequent retrievals
   - Tests show Content Writer +20% but other queries -15% overall
   - Net negative trade-off

3. **Re-ranking/Boosting Issues**
   - Duration score boosting (max_boost=0.25) disrupts carefully tuned BM25 scores
   - Test-type boosting (boost_factor=0.15) too aggressive
   - Even with reduced factors (0.10, 0.08) still hurt overall performance
   - The problem: BM25 ranking is already well-optimized; re-scoring breaks it

4. **Why BM25 Can't Be Beat Easily**
   - Already tuned with α=0.39 (optimal hybrid weight)
   - Dataset has only 10 queries (limited signal for tuning)
   - Each query has 5-10 relevant items (sparse relevance)
   - BM25 naturally handles keywords well; adding synonyms dilutes signal

## Recommendations

### ✅ Keep: Modular Code Structure

All Phase 3 code is well-structured and reusable. Keep modules for future iterations:

```python
from shlrec.phase3_mappings import ROLE_EXPANSIONS
from shlrec.query_expansion import QueryExpander
from shlrec.duration_scoring import parse_duration_from_query
from shlrec.test_type_router import extract_test_type_intent
```

### ❌ Don't Use: Aggressive Re-scoring

- Query expansion: DISABLED (causes retrieval drift)
- Corpus enrichment: DISABLED (vocabulary explosion hurts BM25)
- Score boosting: DISABLED (disrupts ranking)

### 🔄 Future Optimization Paths (Not Implemented)

To actually improve beyond 23.78%, need different approaches:

1. **Semantic Re-ranking** (if Gemini budget allows)
   - Use LLM to score final 10 results
   - Preserve BM25 ranking, use LLM for tie-breaking only
   - Estimated gain: +2-5%

2. **Targeted Corpus Updates** (not general enrichment)
   - For "1 hour" queries: explicitly add "60-minute" assessment descriptions
   - For "Admin" queries: ensure admin descriptions mention "data entry", "clerical"
   - For "Consultant" queries: update catalog with "client-facing" terms
   - UPSIDE: Fixes 3 failing queries without hurting others
   - DOWNSIDE: Requires manual catalog updates

3. **Hybrid Retrieval Fine-tuning**
   - Test α values around 0.39 more granularly (0.38, 0.395, 0.40)
   - Already at local optimum
   - Estimated ceiling: +1-2%

4. **Semantic Embedding Model**
   - Current: all-MiniLM-L6-v2 (general purpose)
   - Option: Fine-tune on SHL domain assessments
   - Option: Use domain-specific model (e.g., for HR)
   - Estimated gain: +3-8%

## Files Modified/Created

**Created (new Phase 3 infrastructure)**:
- `shlrec/phase3_mappings.py` ✅
- `shlrec/corpus_enrichment.py` ✅
- `shlrec/duration_scoring.py` ✅
- `shlrec/query_expansion.py` (modified) ✅
- `shlrec/test_type_router.py` ✅

**Modified**:
- `shlrec/recommender.py` (added Phase 3 imports, integrations disabled)
- `shlrec/indexer.py` (reverted corpus enrichment)

## Conclusion

**Status**: Phase 3 infrastructure implemented but not activated.

**Performance**: Baseline maintained at **23.78% Recall@10, 16.74% MAP@10**

**Next Steps**:
1. ✅ Code is modular and reusable for future iterations
2. ⏭️ Consider semantic re-ranking or targeted corpus updates
3. ⏸️ Hold aggressive phase 3 features until we have larger training set or better tuning data

---

**Date**: December 18, 2025  
**Status**: Phase 3 modules built, features disabled to preserve performance
