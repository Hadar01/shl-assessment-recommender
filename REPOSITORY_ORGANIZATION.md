# Repository Organization Guide

## 🗂️ How This Repository is Organized

This repository is organized for **clarity and ease of navigation**. Here's how to understand the structure:

---

## 📍 Top-Level Organization

```
shl_recommender_starter/
├── README.md                   ← START HERE (project overview)
├── docs/                       ← DOCUMENTATION (organized by topic)
├── shlrec/                     ← SOURCE CODE (core engine)
├── api/                        ← REST API
├── ui/                         ← USER INTERFACE
├── scripts/                    ← DATA PIPELINES
├── data/                       ← DATA STORAGE
└── Configuration files (.env.example, pyproject.toml, requirements.txt)
```

---

## 🚀 Quick Start Path

**If you're new to this project, follow this path:**

1. **Read:** [README.md](./README.md) (5 minutes)
   - What the project does
   - Quick start commands
   - Architecture overview

2. **Setup:** [docs/setup/QUICK_START.md](./docs/setup/QUICK_START.md) (10 minutes)
   - Install dependencies
   - Run API or UI
   - Test everything works

3. **Explore:** [docs/INDEX.md](./docs/INDEX.md) (10 minutes)
   - Navigate all documentation
   - Find what you need
   - Understand the flow

---

## 📚 Documentation Structure

All documentation organized in `docs/` folder:

```
docs/
├── INDEX.md                    ← Navigation hub (start here after README)
│
├── setup/                      ← Getting started & deployment
│   └── QUICK_START.md         # 5-minute setup guide
│
├── architecture/               ← System design & code structure
│   ├── SYSTEM_DESIGN.md       # High-level architecture
│   └── CODE_STRUCTURE.md      # Module organization & data flow
│
├── evaluation/                 ← Performance & metrics
│   └── METRICS.md             # Performance analysis & optimization history
│
├── development/                ← For contributors (optional)
│   └── (Future guides)
│
└── submission/                 ← Submission materials
    └── DELIVERABLES.md        # Verification checklist & contents
```

---

## 💻 Source Code Structure

All executable code in these folders:

```
shlrec/                   ← CORE RECOMMENDATION ENGINE
├── recommender.py       # Main orchestrator (entry point)
├── retrieval.py         # Hybrid search (BM25 + semantic)
├── indexer.py           # Index construction & loading
├── balancing.py         # K/P test balancing
├── llm_gemini.py        # LLM integration (optional)
├── settings.py          # Configuration management
└── utils.py             # Utility functions

api/                      ← REST API
└── main.py              # FastAPI server with /recommend endpoint

ui/                       ← USER INTERFACES
└── streamlit_app.py     # Interactive dashboard

scripts/                  ← DATA PIPELINES & TOOLS
├── build_index.py       # Build search index
├── scrape_catalog.py    # Scrape assessment catalog
├── evaluate_train.py    # Evaluate performance
└── generate_test_csv.py # Generate predictions
```

---

## 🗃️ Data Storage

```
data/
├── catalog.jsonl            # Assessment catalog (377 items)
├── Gen_AI Dataset.xlsx      # Training set (10 labeled queries)
├── predictions.csv          # Test predictions (90 rows)
└── index/                   # Search index (rebuilt on demand)
    ├── meta.json            # Item metadata
    ├── bm25.pkl             # BM25 model
    ├── embeddings.npy       # Semantic embeddings
    └── corpus_tokens.pkl    # Tokenized corpus
```

---

## 🎯 Finding What You Need

### "I want to understand the system"
1. Read: [README.md](./README.md)
2. Check: [docs/architecture/SYSTEM_DESIGN.md](./docs/architecture/SYSTEM_DESIGN.md)
3. Deep dive: [docs/architecture/CODE_STRUCTURE.md](./docs/architecture/CODE_STRUCTURE.md)

### "I want to run it"
1. Follow: [docs/setup/QUICK_START.md](./docs/setup/QUICK_START.md)
2. Commands: `pip install -r requirements.txt`
3. Start: `python -m uvicorn api.main:app --reload`

### "I want to review the code"
1. Start with: [shlrec/recommender.py](./shlrec/recommender.py)
2. Then read: [shlrec/retrieval.py](./shlrec/retrieval.py)
3. Reference: [docs/architecture/CODE_STRUCTURE.md](./docs/architecture/CODE_STRUCTURE.md)

### "I want to see performance metrics"
1. Check: [docs/evaluation/METRICS.md](./docs/evaluation/METRICS.md)
2. Run: `python -m scripts.evaluate_train --xlsx data/Gen_AI\ Dataset.xlsx --index_dir data/index`

### "I need to verify everything is working"
1. Follow: [docs/submission/DELIVERABLES.md](./docs/submission/DELIVERABLES.md)
2. Run: Quick verification steps provided

### "I want to contribute"
1. Check: [docs/development/](./docs/development/) (when available)
2. Follow: Code quality standards in [docs/architecture/CODE_STRUCTURE.md](./docs/architecture/CODE_STRUCTURE.md)

---

## 🔄 Understanding the Flow

**System Flow:**
```
User Query → API/UI → recommender.py → retrieval.py → balancing.py → Results
                      (orchestrator)     (search)      (filtering)
```

**Documentation Flow:**
```
README.md (project overview)
    ↓
docs/INDEX.md (navigation hub)
    ├→ docs/setup/QUICK_START.md (how to run)
    ├→ docs/architecture/ (system design)
    └→ docs/evaluation/METRICS.md (performance)
```

---

## 📊 File Organization Principles

### By Purpose
| Folder | Purpose | Examples |
|--------|---------|----------|
| `shlrec/` | Core engine | recommender, retrieval, indexing |
| `api/` | REST API | FastAPI server, endpoints |
| `ui/` | User interfaces | Streamlit dashboard |
| `scripts/` | Data pipelines | Build, evaluate, generate |
| `data/` | Data storage | Index, catalog, predictions |
| `docs/` | Documentation | Guides, architecture, metrics |

### By Audience
| Audience | Start Here | Then See |
|----------|-----------|----------|
| End Users | [README.md](./README.md) | [docs/setup/QUICK_START.md](./docs/setup/QUICK_START.md) |
| Developers | [README.md](./README.md) | [docs/architecture/](./docs/architecture/) |
| Reviewers | [docs/INDEX.md](./docs/INDEX.md) | [docs/submission/DELIVERABLES.md](./docs/submission/DELIVERABLES.md) |
| DevOps | [docs/setup/QUICK_START.md](./docs/setup/QUICK_START.md) | Configuration section |

---

## 🎯 Key Entry Points

### For Different Tasks

**Starting the system:**
- API: `python -m uvicorn api.main:app --reload`
- UI: `streamlit run ui/streamlit_app.py`

**Building/updating:**
- Index: `python -m scripts.build_index --catalog data/catalog.jsonl --index_dir data/index`
- Predictions: `python -m scripts.generate_test_csv --xlsx data/Gen_AI\ Dataset.xlsx --index_dir data/index --out predictions.csv`

**Evaluating:**
- Performance: `python -m scripts.evaluate_train --xlsx data/Gen_AI\ Dataset.xlsx --index_dir data/index`

**Understanding code:**
- Main entry: [shlrec/recommender.py](./shlrec/recommender.py)
- Search logic: [shlrec/retrieval.py](./shlrec/retrieval.py)
- Data flow: [docs/architecture/SYSTEM_DESIGN.md](./docs/architecture/SYSTEM_DESIGN.md)

---

## ✅ Navigation Checklist

Use this to verify you understand the repo:

- [ ] I can find the README
- [ ] I can locate the documentation hub (INDEX.md)
- [ ] I can identify core modules (shlrec/)
- [ ] I know where API is (api/main.py)
- [ ] I know where UI is (ui/streamlit_app.py)
- [ ] I can find scripts (scripts/)
- [ ] I know where data is (data/)
- [ ] I can find architecture docs (docs/architecture/)
- [ ] I can find performance metrics (docs/evaluation/)
- [ ] I know what to do next (README → QUICK_START → INDEX)

---

## 🚀 Next Steps

1. **Start here:** [README.md](./README.md)
2. **Then setup:** [docs/setup/QUICK_START.md](./docs/setup/QUICK_START.md)
3. **Navigate docs:** [docs/INDEX.md](./docs/INDEX.md)
4. **Run the system!**

---

**This organization ensures:**
- ✅ Easy to understand (logical folder structure)
- ✅ Easy to navigate (clear documentation index)
- ✅ Easy to find things (consistent organization)
- ✅ Professional presentation (clean layout)

**Last Updated:** December 18, 2025
