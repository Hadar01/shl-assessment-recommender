# SHL Assessment Recommendation System

A production-ready AI-powered recommendation system that suggests the most relevant SHL assessments based on hiring queries, job descriptions, or unstructured input.

**Status:** ✅ Production Ready | **Recall@10:** 23.78% | **Dataset:** 377 real SHL assessments

---

## 📚 Documentation Overview

**New to this project?** Start here:

| What You Want | Go To |
|---------------|--------|
| **Quick setup (5 min)** | [QUICK_START.md](./docs/setup/QUICK_START.md) |
| **Deploy to production** | [DEPLOYMENT.md](./docs/setup/DEPLOYMENT.md) |
| **Understand the system** | [SYSTEM_DESIGN.md](./docs/architecture/SYSTEM_DESIGN.md) |
| **See code organization** | [CODE_STRUCTURE.md](./docs/architecture/CODE_STRUCTURE.md) |
| **Check performance** | [METRICS.md](./docs/evaluation/METRICS.md) |
| **Verify deliverables** | [DELIVERABLES.md](./docs/submission/DELIVERABLES.md) |
| **Full documentation** | [docs/INDEX.md](./docs/INDEX.md) |
| **Repository layout** | [REPOSITORY_ORGANIZATION.md](./REPOSITORY_ORGANIZATION.md) |

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the API Server
```bash
python -m uvicorn api.main:app --reload
```
Visit: **http://localhost:8000/docs** (Interactive API)

### 3. (Optional) Run the Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```
Visit: **http://localhost:8501**

---

## 🏗️ System Architecture

```
User Query → Hybrid Search (BM25 + Embeddings) → Candidate Pool → K/P Balancing → Top 10 Recommendations
             (39% BM25 + 61% Semantic)          (200 results)
```

**Key Features:**
- ✅ **Hybrid Search:** 39% BM25 (keyword) + 61% semantic (meaning)
- ✅ **Fast & Accurate:** ~40ms latency, 23.78% Recall@10
- ✅ **Smart Balancing:** Ensures mix of Knowledge & Practical tests
- ✅ **LLM-Ready:** Optional Gemini integration for advanced features
- ✅ **Well-Documented:** Comprehensive architecture & code guides

---

## 📂 Repository Organization

```
docs/                 ← Documentation (organized by topic)
├── setup/            ← Getting started & deployment  
├── architecture/     ← System design & code structure
├── evaluation/       ← Performance metrics & analysis
└── submission/       ← Deliverables & verification

shlrec/               ← Core recommendation engine
api/                  ← REST API (FastAPI)
ui/                   ← Streamlit dashboard
scripts/              ← Data pipelines & tools
data/                 ← Index, catalog, predictions
```

**See [REPOSITORY_ORGANIZATION.md](./REPOSITORY_ORGANIZATION.md) for detailed layout.**

---

## 🚀 Next Steps

### For Different Audiences:

**👤 End Users / Reviewers:**
1. [QUICK_START.md](./docs/setup/QUICK_START.md) - Setup in 5 minutes
2. [DELIVERABLES.md](./docs/submission/DELIVERABLES.md) - Verify all components

**👨‍💻 Developers:**
1. [SYSTEM_DESIGN.md](./docs/architecture/SYSTEM_DESIGN.md) - Architecture overview
2. [CODE_STRUCTURE.md](./docs/architecture/CODE_STRUCTURE.md) - Code walkthrough
3. Explore: `shlrec/recommender.py` → `shlrec/retrieval.py`

**📊 Data Scientists:**
1. [METRICS.md](./docs/evaluation/METRICS.md) - Performance analysis
2. Run: `python -m scripts.evaluate_train --xlsx data/Gen_AI\ Dataset.xlsx --index_dir data/index`

---

## 📖 Traditional Setup Instructions

### 0) Setup

### Create venv + install deps
```bash
python -m venv .venv
source .venv/bin/activate   # (Windows) .venv\Scripts\activate
pip install -r requirements.txt
```

### Add Gemini API key (Free Tier)
1. Get a Gemini key from Google AI Studio / Gemini API docs.
2. Create `.env` from `.env.example`:
```bash
cp .env.example .env
```
3. Put your key in `.env` as `GEMINI_API_KEY=...`

---

## 1) Scrape the SHL Individual Test Solutions catalog

This step creates `data/catalog.jsonl`.

```bash
python scripts/scrape_catalog.py --out data/catalog.jsonl
```

Notes:
- It scrapes **Individual Test Solutions** (type=1 pages) and ignores pre-packaged job solutions.
- It will **error** if it scraped fewer than 377 items (assignment requirement).

---

## 2) Build the search index

This step builds:
- BM25 index (`data/index/bm25.pkl`)
- SentenceTransformer embeddings (`data/index/embeddings.npy`)
- metadata (`data/index/meta.json`)

```bash
python scripts/build_index.py --catalog data/catalog.jsonl --index_dir data/index
```

---

## 3) Run the API (required for submission)

The assignment requires:
- `GET /health` → `{"status":"healthy"}`
- `POST /recommend` with body `{"query": "..."}`

Start:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Test:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query":"Need a Java developer who can collaborate with stakeholders. Time limit 40 minutes."}'
```

---

## 4) Run Streamlit UI (optional but nice for demo)

```bash
streamlit run ui/streamlit_app.py
```

---

## 5) Evaluate on Train Set (mandatory)

Train/Test file is already placed at: `data/Gen_AI Dataset.xlsx`.

```bash
python scripts/evaluate_train.py --xlsx data/Gen_AI\ Dataset.xlsx --index_dir data/index
```

Outputs Recall@10 and MAP@10 on the labeled Train-Set.

---

## 6) Generate Test predictions CSV (for submission)

```bash
python scripts/generate_test_csv.py --xlsx data/Gen_AI\ Dataset.xlsx --index_dir data/index --out predictions.csv
```

This writes in the required format:
`Query,Assessment_url` with **one row per recommendation**.

---

## Recommended defaults (good baseline)
- Hybrid retrieval = BM25 + embeddings
- Gemini used for **query intent extraction** (K/P mix + duration constraint) with on-disk caching to limit API calls.

You should tune:
- `HYBRID_ALPHA` (weighting BM25 vs embeddings)
- `RERANK_WITH_GEMINI` (off by default; can help but increases calls)

---

## Deployment hints (free tier)
- API: Render / Railway / Fly.io (free tiers change; pick what you have)
- UI: Streamlit Community Cloud

If deploying, set env vars in the platform:
- `GEMINI_API_KEY`
- `INDEX_DIR` (default `data/index`)

---

## Files of interest
- `shlrec/catalog_scraper.py` – scraping logic
- `shlrec/recommender.py` – retrieval + Gemini intent + balancing
- `api/main.py` – required API endpoints
- `scripts/evaluate_train.py` – evaluation (Recall@10, MAP@10)
- `scripts/generate_test_csv.py` – submission CSV generator
