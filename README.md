# SHL Assessment Recommendation Engine (Starter)

This is a **starter project** for SHL's take-home assignment: a recommender that returns **5–10 Individual Test Solutions**
given either a **natural language query** or a **Job Description URL**, exposed via a required FastAPI API.

The assignment requires:
- **Scraping and storing** SHL's product catalog (≥ 377 Individual Test Solutions)
- **LLM or retrieval-based integration**
- **Measurable evaluation** (e.g., Mean Recall@10)
- API endpoints and response schema exactly as specified in the brief (see `data/SHL_assignment.pdf`)

---

## 0) Setup

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
