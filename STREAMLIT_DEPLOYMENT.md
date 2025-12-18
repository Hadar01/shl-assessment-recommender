# Streamlit Cloud Deployment

This project is deployed on **Streamlit Cloud** (FREE).

## Live URLs:

### Main Application
- **Streamlit UI:** https://shl-assessment-recommender.streamlit.app/
- **How to Use:** Enter a hiring query or job description, click "Recommend"

### API (for advanced users)
- **API Endpoint:** POST http://localhost:8000/recommend (local only)
- **Interactive Docs:** http://localhost:8000/docs (local only)

---

## How It's Deployed

The app is automatically deployed from GitHub:
1. Code pushed to https://github.com/Hadar01/shl-assessment-recommender
2. Streamlit Cloud detects changes
3. App redeploys automatically (takes ~2-3 minutes)

---

## To Deploy Yourself

### Prerequisites:
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io)

### Steps:
1. Fork the repo: https://github.com/Hadar01/shl-assessment-recommender
2. Go to https://streamlit.io/cloud
3. Click "New app"
4. Select: Repository → main branch → `ui/streamlit_app.py`
5. Deploy!

---

## Test Cases to Try

Copy-paste these into the app:

### Test 1: Java Developer
```
I need to hire a Java developer who can also lead and communicate with stakeholders.
Looking for assessments under 40 minutes.
```

### Test 2: Python Engineer
```
Python backend engineer with 3+ years experience.
Need technical assessment for data structures and algorithms.
Duration: 60 minutes max.
```

### Test 3: Manager/Leader
```
Hiring for a Project Manager role. Need personality and behavioral assessment.
Must include leadership and teamwork evaluation. 45 minutes max.
```

---

## Performance Metrics

- **Recall@10:** 23.78% (captures ~24% of relevant assessments)
- **MAP@10:** 16.74% (quality-weighted ranking)
- **Dataset:** 377 real SHL assessments
- **Search:** Hybrid (39% BM25 + 61% semantic embeddings)

---

## System Components

### Data Pipeline
- **Scraper:** Collected 377 SHL assessments from www.shl.com
- **Indexer:** Built BM25 + semantic search index

### Recommendation Engine
- **Hybrid Search:** Keyword-based (BM25) + semantic (embeddings)
- **LLM Integration:** Google Gemini for query understanding
- **Filtering:** Duration, remote support, test type constraints
- **Balancing:** K/P (Knowledge & Skills vs Personality & Behavior) mix

### Evaluation
- **Metrics:** Recall@10, MAP@10
- **Test Set:** 10 labeled queries with expert annotations
- **Reproducible:** `python scripts/evaluate_train.py`

---

## Code Structure

```
shlrec/                   ← Core recommendation engine
├── recommender.py        ← Main orchestrator
├── retrieval.py          ← Hybrid search (BM25 + embeddings)
├── llm_gemini.py         ← Query understanding with Gemini
├── balancing_improved.py ← K/P test balancing
└── metrics.py            ← Evaluation metrics

ui/
├── streamlit_app.py      ← Web interface (deployed on Streamlit Cloud)

api/
├── main.py               ← FastAPI server (optional, local testing)

scripts/
├── scrape_catalog.py     ← Web scraper for SHL assessments
├── build_index.py        ← Index builder
└── evaluate_train.py     ← Evaluation on labeled test set

data/
├── catalog.jsonl         ← Raw scraped SHL assessments
└── index/                ← Pre-built search index
```

---

## Questions?

See [README.md](../README.md) for full documentation.
