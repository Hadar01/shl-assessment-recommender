# SHL Assessment Recommender - Documentation Index

## 📚 Repository Structure Overview

```
shl_recommender_starter/
├── README.md                          # Start here - Project overview & quick start
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Project configuration
│
├── shlrec/                           # Core recommendation engine
│   ├── __init__.py
│   ├── recommender.py                # Main orchestrator (entry point)
│   ├── retrieval.py                  # Hybrid search (BM25 + semantic)
│   ├── indexer.py                    # Index construction
│   ├── llm_gemini.py                 # LLM integration (Gemini)
│   ├── balancing.py                  # K/P test balancing
│   ├── settings.py                   # Configuration management
│   └── utils.py                      # Utility functions
│
├── api/                              # REST API
│   └── main.py                       # FastAPI server (/recommend endpoint)
│
├── ui/                               # User interfaces
│   └── streamlit_app.py              # Interactive Streamlit dashboard
│
├── scripts/                          # Data & evaluation pipelines
│   ├── build_index.py                # Build search index
│   ├── scrape_catalog.py             # Scrape SHL catalog
│   ├── evaluate_train.py             # Performance evaluation
│   └── generate_test_csv.py          # Generate predictions
│
├── data/                             # Data directory
│   ├── catalog.jsonl                 # SHL assessment catalog (377 items)
│   ├── Gen_AI Dataset.xlsx           # Training/evaluation set
│   ├── predictions.csv               # Test set predictions
│   └── index/                        # Search index (BM25 + embeddings)
│       ├── meta.json
│       ├── bm25.pkl
│       ├── embeddings.npy
│       └── corpus_tokens.pkl
│
├── docs/                             # Documentation (this folder)
│   ├── INDEX.md                      # You are here
│   ├── setup/                        # Setup & deployment
│   ├── architecture/                 # System design
│   ├── development/                  # Development guides
│   ├── evaluation/                   # Performance & metrics
│   └── submission/                   # Submission materials
│
├── .env.example                      # Configuration template
├── .gitignore                        # Git exclusions
└── predictions.csv                  # Final test predictions

```

---

## 🚀 Quick Navigation by Task

### 1️⃣ **Getting Started**
- **First time here?** → Read [README.md](../README.md)
- **Setup instructions** → See [docs/setup/QUICK_START.md](setup/QUICK_START.md)
- **Install dependencies** → `pip install -r requirements.txt`

### 2️⃣ **Understanding the System**
- **Architecture overview** → [docs/architecture/SYSTEM_DESIGN.md](architecture/SYSTEM_DESIGN.md)
- **How recommendation works** → [docs/architecture/RECOMMENDATION_FLOW.md](architecture/RECOMMENDATION_FLOW.md)
- **Code structure** → [docs/architecture/CODE_STRUCTURE.md](architecture/CODE_STRUCTURE.md)

### 3️⃣ **Running the System**
- **Start API server** → `python -m uvicorn api.main:app --reload`
- **Start Streamlit UI** → `streamlit run ui/streamlit_app.py`
- **Build index** → `python -m scripts.build_index --catalog data/catalog.jsonl --index_dir data/index`
- **Evaluate performance** → `python -m scripts.evaluate_train --xlsx data/Gen_AI\ Dataset.xlsx --index_dir data/index`

### 4️⃣ **Understanding Performance**
- **Evaluation results** → [docs/evaluation/METRICS.md](evaluation/METRICS.md)
- **Performance analysis** → [docs/evaluation/PERFORMANCE_ANALYSIS.md](evaluation/PERFORMANCE_ANALYSIS.md)
- **Optimization history** → [docs/evaluation/OPTIMIZATION_HISTORY.md](evaluation/OPTIMIZATION_HISTORY.md)

### 5️⃣ **Development & Contributing**
- **Development guide** → [docs/development/DEVELOPMENT.md](development/DEVELOPMENT.md)
- **Phase 3 experimental features** → [docs/development/PHASE3_ANALYSIS.md](development/PHASE3_ANALYSIS.md)
- **Code improvements** → [docs/development/IMPROVEMENTS.md](development/IMPROVEMENTS.md)

### 6️⃣ **Submission Materials**
- **Submission checklist** → [docs/submission/DELIVERABLES.md](submission/DELIVERABLES.md)
- **Verification checklist** → [docs/submission/VERIFICATION.md](submission/VERIFICATION.md)
- **GitHub instructions** → [docs/submission/GITHUB.md](submission/GITHUB.md)

---

## 📊 System Flow

```
User Query
    ↓
┌─────────────────────────────────────────────────────────────┐
│               shlrec/recommender.py (Orchestrator)          │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├─→ Query Preprocessing
    ├─→ Hybrid Search (retrieval.py)
    │   ├─→ BM25 Search (Alpha=0.39 → 39% weight)
    │   └─→ Semantic Search (1-Alpha=0.61 → 61% weight)
    ├─→ Candidate Pool Retrieval (Top 200)
    ├─→ Test Type Filtering & K/P Balancing (balancing.py)
    └─→ Final Ranking
    ↓
Recommendations (Top 10 Assessments)
```

---

## 🔑 Key Files & Their Purpose

### Core Engine
| File | Purpose | Key Functions |
|------|---------|---|
| `shlrec/recommender.py` | Main orchestrator | `recommend()` - entry point |
| `shlrec/retrieval.py` | Hybrid search | `hybrid_search()`, `bm25_search()`, `semantic_search()` |
| `shlrec/indexer.py` | Index builder | `build_index()`, `load_index()` |
| `shlrec/balancing.py` | K/P balancing | `balance_k_p_assessments()` |

### Integration & Configuration
| File | Purpose | Key Functions |
|------|---------|---|
| `shlrec/llm_gemini.py` | LLM interface | `extract_intent()`, `rerank_with_gemini()` |
| `shlrec/settings.py` | Config management | `Settings` class, env variables |
| `shlrec/utils.py` | Utilities | Helper functions |

### APIs & UIs
| File | Purpose | Key Endpoints/Features |
|------|---------|---|
| `api/main.py` | REST API | `POST /recommend` |
| `ui/streamlit_app.py` | Dashboard | Interactive recommendation UI |

### Data Pipelines
| File | Purpose | Inputs/Outputs |
|------|---------|---|
| `scripts/build_index.py` | Index building | `.jsonl` catalog → Search index |
| `scripts/scrape_catalog.py` | Data collection | SHL website → `.jsonl` catalog |
| `scripts/evaluate_train.py` | Performance eval | `.xlsx` test set → Metrics |
| `scripts/generate_test_csv.py` | Prediction gen | Test set → `predictions.csv` |

---

## 📈 Performance Metrics

**Current Performance:**
- **Recall@10:** 23.78%
- **MAP@10:** 16.74%
- **Configuration:** HYBRID_ALPHA=0.39, CANDIDATE_POOL=200

See [docs/evaluation/METRICS.md](evaluation/METRICS.md) for detailed breakdown.

---

## 🔧 Configuration

### Environment Variables
See `.env.example` for all available settings:

```env
HYBRID_ALPHA=0.39              # 39% BM25, 61% semantic
CANDIDATE_POOL=200            # Top candidates before filtering
RERANK_WITH_GEMINI=0          # Disable LLM reranking
GEMINI_API_KEY=...            # Optional: for LLM features
INDEX_DIR=data/index          # Search index location
```

---

## 🎯 Common Workflows

### Scenario 1: Adding New Assessments
1. Update `data/catalog.jsonl` with new entries
2. Rebuild index: `python -m scripts.build_index ...`
3. Test with UI: `streamlit run ui/streamlit_app.py`

### Scenario 2: Improving Performance
1. Review metrics: [docs/evaluation/METRICS.md](evaluation/METRICS.md)
2. Check optimization history: [docs/evaluation/OPTIMIZATION_HISTORY.md](evaluation/OPTIMIZATION_HISTORY.md)
3. Make changes & evaluate: `python -m scripts.evaluate_train ...`

### Scenario 3: Deploying to Production
1. Set `.env` with production values
2. Build index: `python -m scripts.build_index ...`
3. Start API: `python -m uvicorn api.main:app --reload`
4. See [docs/setup/DEPLOYMENT.md](setup/DEPLOYMENT.md)

---

## 📚 Documentation Organization

### By Purpose:
- **Setup** (`docs/setup/`) - Installation, deployment, configuration
- **Architecture** (`docs/architecture/`) - System design, data flow, code structure
- **Development** (`docs/development/`) - Contributing, improvements, experimentation
- **Evaluation** (`docs/evaluation/`) - Metrics, analysis, performance tuning
- **Submission** (`docs/submission/`) - Deliverables, verification, GitHub

### By Audience:
- **End Users** → Start with README.md, then `docs/setup/QUICK_START.md`
- **Developers** → Check `docs/architecture/` and `docs/development/`
- **Reviewers** → See `docs/submission/DELIVERABLES.md` and `docs/evaluation/METRICS.md`
- **DevOps** → Read `docs/setup/DEPLOYMENT.md`

---

## 🚀 Next Steps

1. **New here?** Read [README.md](../README.md) first
2. **Want to run it?** Follow [docs/setup/QUICK_START.md](setup/QUICK_START.md)
3. **Need details?** Browse [docs/architecture/](architecture/)
4. **Reviewing?** Check [docs/submission/DELIVERABLES.md](submission/DELIVERABLES.md)

---

**Last Updated:** December 18, 2025  
**Version:** 1.0 - Production Ready
