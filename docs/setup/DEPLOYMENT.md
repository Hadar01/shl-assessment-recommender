# Deployment Guide

## 🚀 Quick Deployment Options

Choose your preferred deployment method:

---

## 1️⃣ **Local Deployment** (Development)

### Start API Server
```bash
pip install -r requirements.txt
python -m uvicorn api.main:app --reload
```

**Access:** http://localhost:8000/docs

### Start Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```

**Access:** http://localhost:8501

---

## 2️⃣ **Docker Deployment** (Recommended)

### Build Docker Image
```bash
docker build -t shl-recommender .
```

### Run Container
```bash
docker run -p 8000:8000 shl-recommender
```

**Access:** http://localhost:8000/docs

---

## 3️⃣ **Docker Compose** (Full Stack)

### Start All Services
```bash
docker-compose up
```

**Services:**
- API: http://localhost:8000/docs
- UI: http://localhost:8501

---

## 4️⃣ **Cloud Deployment**

### Railway (Easiest)
1. Push to GitHub
2. Visit https://railway.app
3. Connect GitHub repository
4. Deploy automatically

### Heroku (Traditional)
```bash
heroku login
heroku create shl-recommender
git push heroku main
```

### AWS/Azure/GCP
See cloud-specific guides in docs/deployment/

---

## 5️⃣ **Environment Setup**

### Create `.env` file
```bash
cp .env.example .env
```

### Set Production Variables
```env
HYBRID_ALPHA=0.39
CANDIDATE_POOL=200
INDEX_DIR=data/index
GEMINI_API_KEY=your_key  # Optional
```

---

## 📊 Performance Requirements

- **CPU:** 1+ cores
- **RAM:** 2+ GB (index loaded in memory)
- **Disk:** 200+ MB (for index)
- **Network:** Needed for Gemini API calls (optional)

---

## ✅ Verification After Deployment

### Test API Health
```bash
curl http://localhost:8000/health
```

### Test Recommendation
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Data Scientist",
    "skills": "Python, Machine Learning"
  }'
```

### Check Logs
```bash
# Docker
docker logs <container_id>

# Local
# Check console output
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Use different port
python -m uvicorn api.main:app --reload --port 8001
```

### Index Not Found
```bash
# Rebuild index
python -m scripts.build_index --catalog data/catalog.jsonl --index_dir data/index
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📈 Scaling

### For High Traffic
1. Use gunicorn with multiple workers
2. Add caching layer (Redis)
3. Load balance across multiple instances

### Configuration
```bash
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 🔐 Security Best Practices

- ✅ Use HTTPS in production
- ✅ Set strong CORS policies
- ✅ Rotate API keys regularly
- ✅ Use environment variables for secrets
- ✅ Enable request rate limiting
- ✅ Monitor API usage

---

**See:** docs/deployment/ for more detailed guides
