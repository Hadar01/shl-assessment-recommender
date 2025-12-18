# Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Prerequisites
- Python 3.10+
- pip (Python package manager)
- Optional: GitHub account for code review

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download & Build Index
The index is pre-built in `data/index/`. Skip to next step unless you need to rebuild:

```bash
# Build fresh index (optional)
python -m scripts.build_index \
  --catalog data/catalog.jsonl \
  --index_dir data/index
```

### 4. Run the API Server
```bash
python -m uvicorn api.main:app --reload
```

Visit: **http://localhost:8000/docs** (Interactive Swagger UI)

### 5. Test the API
**Example request:**
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Data Scientist",
    "skills": "Python, Machine Learning, Statistical Analysis"
  }'
```

### 6. (Optional) Run Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```

Visit: **http://localhost:8501**

---

## 📊 Evaluate Performance

```bash
python -m scripts.evaluate_train \
  --xlsx data/Gen_AI\ Dataset.xlsx \
  --index_dir data/index
```

Expected output: **Recall@10: 23.78%**, **MAP@10: 16.74%**

---

## 📁 Configuration

### Environment Variables
Copy and edit `.env`:
```bash
cp .env.example .env
```

**Key settings:**
```env
HYBRID_ALPHA=0.39              # Search tuning (0.39 = 39% BM25, 61% semantic)
CANDIDATE_POOL=200            # Top candidates before filtering
GEMINI_API_KEY=your_key        # Optional: for LLM features
INDEX_DIR=data/index           # Index location
```

---

## 🔍 Troubleshooting

### Issue: ModuleNotFoundError
```bash
# Solution: Make sure you're in the correct directory
cd c:\Users\admin\Desktop\task\shl_recommender_starter

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Port 8000 already in use
```bash
# Run on different port
python -m uvicorn api.main:app --reload --port 8001
```

### Issue: GEMINI_API_KEY error
This is optional. The system works without it.
Leave blank or remove from `.env`

---

## 📚 Next Steps

- **API Documentation:** http://localhost:8000/docs (when running)
- **Architecture Details:** See `docs/architecture/`
- **Performance Analysis:** See `docs/evaluation/METRICS.md`
- **Full Documentation:** See `docs/INDEX.md`

---

**Need help?** Check the troubleshooting section above or see `README.md`
