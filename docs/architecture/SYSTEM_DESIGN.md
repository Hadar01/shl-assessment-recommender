# System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                         │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI (/recommend endpoint)    │    Streamlit Dashboard      │
└──────────────────────┬──────────────────────────────────┬──────┘
                       │                                  │
                       └──────────────┬───────────────────┘
                                      ↓
                    ┌──────────────────────────────┐
                    │   recommender.py             │
                    │   (Main Orchestrator)        │
                    └──────────────┬───────────────┘
                                   ↓
         ┌─────────────────────────────────────────┐
         │         Retrieval System                │
         ├─────────────────────────────────────────┤
         │  retrieval.py: Hybrid Search            │
         │  • BM25 Search (39% weight)             │
         │  • Semantic Search (61% weight)         │
         │  • Score Fusion                         │
         └──────────┬──────────────────────────┬───┘
                    │                          │
           ┌────────▼─────────┐      ┌─────────▼──────────┐
           │  BM25 Index      │      │ Semantic Index     │
           │  (sparse search) │      │ (embeddings)       │
           └────────┬─────────┘      └─────────┬──────────┘
                    │                          │
                    └──────────┬───────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  Candidate Pool      │
                    │  (Top 200 results)   │
                    └──────────┬───────────┘
                               ↓
            ┌──────────────────────────────────┐
            │  Post-Processing                 │
            ├──────────────────────────────────┤
            │  • Test Type Filtering           │
            │  • K/P Balance (balancing.py)    │
            │  • LLM Reranking (optional)      │
            └──────────────┬───────────────────┘
                           ↓
                ┌───────────────────────┐
                │  Final Rankings       │
                │  (Top 10 Assessments) │
                └───────────────────────┘
```

---

## 📋 Component Details

### 1. **Input Layer: User Interfaces**

#### FastAPI Server (`api/main.py`)
- **Endpoint:** `POST /recommend`
- **Input:** Job title, skills, experience
- **Output:** JSON array of recommended assessments
- **Port:** 8000 (default)

#### Streamlit UI (`ui/streamlit_app.py`)
- **Interactive dashboard** for easy testing
- **Real-time recommendations**
- **Visualization of assessment details**
- **Port:** 8501 (default)

---

### 2. **Orchestration Layer: recommender.py**

**Main entry point** that coordinates the entire flow:

```python
def recommend(
    job_title: str,
    skills: str,
    experience_level: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main recommendation function
    1. Preprocess query
    2. Call hybrid search
    3. Apply filtering & balancing
    4. Return top 10 recommendations
    """
```

**Key responsibilities:**
- Query preprocessing
- Calling retrieval module
- Applying business logic (K/P balancing)
- Formatting results

---

### 3. **Retrieval Layer: retrieval.py**

**Hybrid search** combining BM25 and semantic search:

#### BM25 Search (39% weight)
```
Query → Tokenize → BM25 Index → Sparse Ranking
```
- Keyword-based matching
- Fast, interpretable
- Good for exact matches

#### Semantic Search (61% weight)
```
Query → Embed (sentence-transformers) → Similarity Search → Dense Ranking
```
- Meaning-based matching
- Captures intent
- Good for paraphrasing

#### Score Fusion
```
final_score = 0.39 * bm25_score + 0.61 * semantic_score
```

---

### 4. **Index Layer**

Located in `data/index/`:

| File | Purpose | Size |
|------|---------|------|
| `meta.json` | Item metadata (377 assessments) | ~200KB |
| `bm25.pkl` | BM25 model (pickled) | ~15MB |
| `embeddings.npy` | Semantic embeddings (numpy) | ~50MB |
| `corpus_tokens.pkl` | Tokenized corpus | ~5MB |

**Building the index:**
```bash
python -m scripts.build_index \
  --catalog data/catalog.jsonl \
  --index_dir data/index
```

---

### 5. **Post-Processing Layer**

#### Filtering & Balancing (`balancing.py`)
- **Test Type Filtering:** Only relevant assessment types
- **K/P Balance:** Ensure mix of Knowledge & Practical tests
- **Logic:**
  ```python
  balanced = balance_k_p_assessments(candidates, top_k=10)
  ```

#### Optional LLM Reranking (`llm_gemini.py`)
- Uses Gemini API to understand job intent
- Re-ranks results if enabled (currently disabled)
- Conservative approach: only rerank if confident

---

## 🔄 Data Flow Example

```
User Input: "Senior Data Scientist, Python, ML"
    ↓
Preprocessing: Split into tokens, normalize
    ↓
BM25 Search:
    • Find "Data" → matches ~150 assessments
    • Find "Scientist" → matches ~50 assessments
    • Rank by TF-IDF → Top candidates
    ↓
Semantic Search:
    • Embed query using sentence-transformers
    • Find similar assessments via embeddings
    • Rank by cosine similarity → Top candidates
    ↓
Score Fusion:
    • Combine scores: 0.39*bm25 + 0.61*semantic
    • Re-rank candidates
    ↓
Get Top 200 Candidates
    ↓
Balancing:
    • Filter by relevant test types
    • Ensure K/P mix
    ↓
Get Top 10 Final Results
    ↓
Return to User (via API or UI)
```

---

## 📊 Performance Characteristics

| Component | Time | Throughput |
|-----------|------|-----------|
| Query Preprocessing | <1ms | N/A |
| BM25 Search | 5-10ms | ~100 queries/sec |
| Semantic Search | 20-50ms | ~20 queries/sec |
| Balancing | <1ms | N/A |
| **Total E2E** | **30-60ms** | **~15-20 queries/sec** |

**Index Loading:** ~500ms (one-time on startup)

---

## 🔧 Configuration Impact

### HYBRID_ALPHA Parameter
Controls BM25 vs Semantic weight:

```
HYBRID_ALPHA = 0.39
├─ 39% weight to BM25 (keyword matching)
└─ 61% weight to Semantic (meaning matching)
```

**Tuning:**
- **α too low (e.g., 0.1):** Semantic dominates, may miss keywords
- **α optimal (0.39):** Best balance, empirically optimized
- **α too high (e.g., 0.8):** BM25 dominates, misses intent

**Current value 0.39 achieved 23.78% Recall@10** through grid search

---

## 🔌 Extension Points

### Adding New Retrieval Methods
1. Implement search function in `retrieval.py`
2. Add score fusion logic
3. Update `recommender.py` to call new method

### Customizing Post-Processing
1. Modify `balancing.py` for different balance strategies
2. Update filters based on business rules

### Using Different LLM
1. Implement new adapter in `llm_gemini.py`
2. Update `settings.py` for LLM config
3. Call from `recommender.py`

---

## 📚 Related Documentation
- **Code Structure:** See `CODE_STRUCTURE.md`
- **Recommendation Flow:** See `RECOMMENDATION_FLOW.md`
- **Performance Analysis:** See `docs/evaluation/METRICS.md`

---

**Last Updated:** December 18, 2025  
**Version:** 1.0 - Production Ready
