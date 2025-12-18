# Code Structure & Organization

## 📂 Directory Tree

```
shl_recommender_starter/
│
├── shlrec/                      # CORE RECOMMENDATION ENGINE
│   ├── __init__.py
│   ├── recommender.py           # 🎯 Entry point - orchestrates flow
│   ├── retrieval.py             # 🔍 Hybrid search (BM25 + semantic)
│   ├── indexer.py               # 📑 Index construction & loading
│   ├── llm_gemini.py            # 🤖 LLM integration (optional)
│   ├── balancing.py             # ⚖️  K/P test balancing
│   ├── settings.py              # ⚙️  Configuration management
│   └── utils.py                 # 🔧 Utility functions
│
├── api/                         # REST API LAYER
│   └── main.py                  # FastAPI server + /recommend endpoint
│
├── ui/                          # USER INTERFACES
│   └── streamlit_app.py         # Streamlit dashboard
│
├── scripts/                     # DATA PIPELINES & TOOLS
│   ├── build_index.py           # Build search index
│   ├── scrape_catalog.py        # Scrape SHL catalog
│   ├── evaluate_train.py        # Performance evaluation
│   └── generate_test_csv.py     # Generate predictions
│
├── data/                        # DATA STORAGE
│   ├── catalog.jsonl            # Assessment catalog (377 items)
│   ├── Gen_AI Dataset.xlsx      # Training/eval set (10 queries)
│   ├── predictions.csv          # Test predictions (90 queries)
│   └── index/                   # Search index
│       ├── meta.json
│       ├── bm25.pkl
│       ├── embeddings.npy
│       └── corpus_tokens.pkl
│
└── docs/                        # DOCUMENTATION (THIS FOLDER)
    ├── INDEX.md                 # You are here!
    ├── setup/
    │   └── QUICK_START.md
    ├── architecture/
    │   ├── SYSTEM_DESIGN.md     # High-level architecture
    │   └── CODE_STRUCTURE.md    # This file
    ├── development/
    ├── evaluation/
    └── submission/
```

---

## 🎯 Core Module: shlrec/

### 1. **recommender.py** (Main Orchestrator)
**Responsibility:** Coordinate the entire recommendation flow

```python
class Recommender:
    def recommend(
        job_title: str,
        skills: str,
        experience_level: Optional[str]
    ) -> Dict[str, Any]:
        """Main entry point for recommendations"""
        
        # 1. Initialize if needed
        self._lazy_load()
        
        # 2. Search
        candidates = self.retrieval.hybrid_search(...)
        
        # 3. Balance
        balanced = self.balancer.balance_k_p_assessments(...)
        
        # 4. Return top 10
        return format_results(balanced[:10])
```

**Key Methods:**
- `recommend()` - Main entry point
- `_lazy_load()` - Initialize components
- `_create_retrieval()` - Setup retrieval system

**Dependencies:**
- `retrieval.py` - Hybrid search
- `balancing.py` - K/P balancing
- `settings.py` - Configuration

---

### 2. **retrieval.py** (Hybrid Search)
**Responsibility:** Combined BM25 + semantic search

```python
class HybridRetrieval:
    def hybrid_search(
        query: str,
        top_k: int = 200
    ) -> List[Tuple[int, float]]:
        """Hybrid search: BM25 + semantic"""
        
        # 1. BM25 search (39% weight)
        bm25_results = self.bm25_search(query)
        
        # 2. Semantic search (61% weight)
        semantic_results = self.semantic_search(query)
        
        # 3. Fuse scores
        fused = self._fuse_scores(bm25_results, semantic_results)
        
        return fused[:top_k]
```

**Key Methods:**
- `hybrid_search()` - Main search entry point
- `bm25_search()` - Keyword-based search
- `semantic_search()` - Meaning-based search
- `_fuse_scores()` - Combine scores (α = 0.39)

**Key Constants:**
- `HYBRID_ALPHA = 0.39` - BM25 weight
- `SEMANTIC_WEIGHT = 0.61` - Semantic weight

---

### 3. **indexer.py** (Index Management)
**Responsibility:** Build, load, and manage search index

```python
def build_index(
    catalog_path: str,
    index_dir: str
):
    """Build fresh index from catalog"""
    
    # 1. Load catalog (catalog.jsonl)
    items = load_catalog(catalog_path)
    
    # 2. Build corpus (name + description + metadata)
    corpus = [item['name'] + ' ' + item['description'] for item in items]
    
    # 3. Build BM25 index
    bm25_model = build_bm25(corpus)
    
    # 4. Build embeddings (sentence-transformers)
    embeddings = embed_corpus(corpus)
    
    # 5. Save all to index_dir
    save_index(index_dir, bm25_model, embeddings)
```

**Key Functions:**
- `build_index()` - Full index pipeline
- `load_index()` - Load pre-built index
- `build_bm25()` - Create BM25 model
- `embed_corpus()` - Create semantic embeddings

**Output Files:**
- `meta.json` - Item metadata
- `bm25.pkl` - BM25 model
- `embeddings.npy` - Embeddings matrix
- `corpus_tokens.pkl` - Tokenized corpus

---

### 4. **balancing.py** (K/P Balancing)
**Responsibility:** Ensure diverse test types in results

```python
def balance_k_p_assessments(
    candidates: List[Assessment],
    top_k: int = 10
) -> List[Assessment]:
    """Balance Knowledge (K) and Practical (P) tests"""
    
    balanced = []
    k_count, p_count = 0, 0
    max_per_type = top_k // 2
    
    for assessment in candidates:
        # Alternate K and P
        if assessment.test_type == 'K' and k_count < max_per_type:
            balanced.append(assessment)
            k_count += 1
        elif assessment.test_type == 'P' and p_count < max_per_type:
            balanced.append(assessment)
            p_count += 1
        
        if len(balanced) == top_k:
            break
    
    return balanced
```

**Key Functions:**
- `balance_k_p_assessments()` - Main balancing logic
- `filter_by_test_type()` - Filter assessments

---

### 5. **settings.py** (Configuration)
**Responsibility:** Centralized configuration management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Retrieval
    hybrid_alpha: float = 0.39
    candidate_pool: int = 200
    
    # LLM (optional)
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash"
    rerank_with_gemini: bool = False
    
    # Paths
    index_dir: str = "data/index"
    catalog_path: str = "data/catalog.jsonl"
    
    class Config:
        env_file = ".env"
```

**Key Variables:**
- `HYBRID_ALPHA` - BM25 weight (currently 0.39)
- `CANDIDATE_POOL` - Top candidates before filtering
- `GEMINI_API_KEY` - Optional LLM key
- `INDEX_DIR` - Index location

---

### 6. **llm_gemini.py** (LLM Integration - Optional)
**Responsibility:** LLM-based intent extraction (currently disabled)

```python
class GeminiIntentExtractor:
    def extract_intent(query: str) -> Dict[str, Any]:
        """Use Gemini to understand job query"""
        
        # Disabled in production (RERANK_WITH_GEMINI = 0)
        # Can be enabled for improved ranking
        
        prompt = f"Analyze this job query: {query}"
        response = gemini_api.generate(prompt)
        return parse_response(response)
```

**Status:** Optional feature, disabled in current production

---

### 7. **utils.py** (Utilities)
**Responsibility:** Common utility functions

```python
# Text processing
def preprocess_text(text: str) -> str:
    """Normalize and clean text"""

# Format output
def format_assessment(item: Dict) -> Dict:
    """Format assessment for API response"""

# Logging
def log_recommendation(query, results):
    """Log recommendation for analysis"""
```

---

## 🔌 API Layer: api/

### main.py (FastAPI Server)
**Responsibility:** REST API endpoint for recommendations

```python
from fastapi import FastAPI
from shlrec.recommender import Recommender

app = FastAPI()
recommender = Recommender()

@app.post("/recommend")
async def recommend(request: RecommendRequest) -> RecommendResponse:
    """
    POST /recommend
    
    Request:
    {
        "job_title": "Senior Data Scientist",
        "skills": "Python, Machine Learning",
        "experience_level": "senior"
    }
    
    Response:
    {
        "recommendations": [
            {
                "assessment_id": 1,
                "name": "...",
                "description": "...",
                ...
            },
            ...
        ]
    }
    """
    return recommender.recommend(
        job_title=request.job_title,
        skills=request.skills,
        experience_level=request.experience_level
    )
```

**Endpoint:**
- `POST /recommend` - Main recommendation endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /health` - Health check (if implemented)

---

## 🎨 UI Layer: ui/

### streamlit_app.py (Interactive Dashboard)
**Responsibility:** User-friendly web interface

**Features:**
- Text input for job title, skills, experience
- Real-time recommendations
- Assessment details (description, duration, type)
- Performance metrics display
- API integration

**Runs on:** `http://localhost:8501`

---

## 🔄 Scripts: scripts/

### build_index.py
```bash
python -m scripts.build_index \
  --catalog data/catalog.jsonl \
  --index_dir data/index
```

### evaluate_train.py
```bash
python -m scripts.evaluate_train \
  --xlsx data/Gen_AI\ Dataset.xlsx \
  --index_dir data/index
```

### generate_test_csv.py
```bash
python -m scripts.generate_test_csv \
  --xlsx data/Gen_AI\ Dataset.xlsx \
  --index_dir data/index \
  --out predictions.csv
```

---

## 🔗 Data Flow Between Modules

```
User Query
    ↓
[api/main.py] 
    ↓
[shlrec/recommender.py]
    ↓
[shlrec/retrieval.py]
    ├─→ [shlrec/indexer.py] - Load index
    ├─→ BM25 search
    └─→ Semantic search
    ↓
[shlrec/balancing.py]
    ├─→ Filter by test type
    └─→ K/P balance
    ↓
[shlrec/llm_gemini.py] (optional)
    ↓
Formatted Response
    ↓
[api/main.py] / [ui/streamlit_app.py]
    ↓
User
```

---

## 📊 Module Dependencies

```
recommender.py (orchestrator)
├── retrieval.py (search)
│   ├── indexer.py (index management)
│   ├── settings.py (config)
│   └── utils.py (helpers)
├── balancing.py (filtering)
├── llm_gemini.py (optional LLM)
└── settings.py (config)

api/main.py
└── recommender.py (through initialization)

ui/streamlit_app.py
├── recommender.py (inference)
└── requests library (API calls)
```

---

## 🚀 Module Loading Sequence

```
1. settings.py loads (configuration)
2. indexer.py loads & initializes index
3. retrieval.py wraps BM25 + embeddings
4. recommender.py assembles pipeline
5. API/UI layers call recommender
```

---

## ✅ Code Quality Standards

All modules follow:
- ✅ Type hints on all functions
- ✅ Comprehensive docstrings
- ✅ Error handling
- ✅ Configuration-driven behavior
- ✅ DRY principle
- ✅ Modular design

---

**Last Updated:** December 18, 2025  
**Version:** 1.0 - Production Ready
