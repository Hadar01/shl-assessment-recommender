# Production Deployment Guide

## 🚀 Deployment Overview

This guide covers deploying the SHL Assessment Recommender to production environments.

---

## 📋 Pre-Deployment Checklist

- [ ] Index built and tested locally
- [ ] Environment variables configured
- [ ] API tested with sample requests
- [ ] Dependencies pinned in requirements.txt
- [ ] Code reviewed and tested
- [ ] Database/index accessible
- [ ] Monitoring configured
- [ ] Backup strategy in place

---

## 🐳 Docker Deployment (Recommended)

### Build Image
```bash
docker build -t shl-recommender:latest .
docker tag shl-recommender:latest shl-recommender:1.0.0
```

### Run Single Container
```bash
docker run -d \
  --name shl-api \
  -p 8000:8000 \
  -e HYBRID_ALPHA=0.39 \
  -e CANDIDATE_POOL=200 \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  -v $(pwd)/data:/app/data \
  shl-recommender:latest
```

### Run with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

**Access:**
- API: http://localhost:8000/docs
- UI: http://localhost:8501

---

## ☁️ Cloud Platform Deployments

### **Railway (Fastest)**

1. **Connect GitHub**
   - Visit https://railway.app
   - Connect your GitHub account
   - Select repository

2. **Configure**
   - Railway auto-detects Dockerfile
   - Add environment variables
   - Set domain

3. **Deploy**
   ```bash
   # Just push to GitHub
   git push origin main
   ```

4. **Access**
   - API: `https://your-railway-app.up.railway.app`

---

### **Heroku**

1. **Install Heroku CLI**
   ```bash
   heroku login
   ```

2. **Create App**
   ```bash
   heroku create shl-recommender
   ```

3. **Add Buildpack**
   ```bash
   heroku buildpacks:add heroku/python
   heroku buildpacks:add heroku/docker
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set HYBRID_ALPHA=0.39
   heroku config:set CANDIDATE_POOL=200
   heroku config:set GEMINI_API_KEY=$GEMINI_API_KEY
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Monitor**
   ```bash
   heroku logs --tail
   ```

---

### **AWS EC2**

1. **Launch Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance: t3.medium (2GB RAM, 1 vCPU)
   - Storage: 20GB SSD

2. **Setup**
   ```bash
   ssh -i key.pem ubuntu@instance-ip
   
   sudo apt-get update
   sudo apt-get install -y python3.12 python3-pip git docker.io
   
   git clone https://github.com/Hadar01/shl-assessment-recommender.git
   cd shl-assessment-recommender
   
   pip install -r requirements.txt
   ```

3. **Run with Supervisor**
   ```bash
   sudo apt-get install supervisor
   
   # Create /etc/supervisor/conf.d/shl-recommender.conf
   sudo systemctl restart supervisor
   ```

4. **Setup Nginx Reverse Proxy**
   ```bash
   sudo apt-get install nginx
   
   # Configure /etc/nginx/sites-available/shl-recommender
   sudo systemctl restart nginx
   ```

---

### **Google Cloud Run**

1. **Setup**
   ```bash
   gcloud auth login
   gcloud config set project PROJECT_ID
   ```

2. **Build and Push**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/shl-recommender
   ```

3. **Deploy**
   ```bash
   gcloud run deploy shl-recommender \
     --image gcr.io/PROJECT_ID/shl-recommender \
     --platform managed \
     --region us-central1 \
     --set-env-vars HYBRID_ALPHA=0.39,CANDIDATE_POOL=200 \
     --memory 2Gi \
     --cpu 1
   ```

---

## 🔧 Configuration for Production

### `.env` Production Settings
```env
# Search Configuration
HYBRID_ALPHA=0.39
CANDIDATE_POOL=200

# Paths
INDEX_DIR=/app/data/index
CATALOG_PATH=/app/data/catalog.jsonl

# LLM (Optional)
GEMINI_API_KEY=your_production_key
GEMINI_MODEL=gemini-2.0-flash
RERANK_WITH_GEMINI=0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# API
API_TIMEOUT=30
MAX_WORKERS=4
```

---

## 📊 Monitoring & Logging

### Health Check
```bash
curl -X GET "http://your-domain:8000/health"
```

### View Logs
```bash
# Docker
docker logs -f shl-api

# Heroku
heroku logs --tail

# AWS EC2
tail -f /var/log/shl-recommender.log
```

### Monitor Performance
```bash
# Inside container
python -m scripts.evaluate_train \
  --xlsx data/Gen_AI\ Dataset.xlsx \
  --index_dir data/index
```

---

## 🔐 Security Best Practices

### HTTPS/TLS
- Enable SSL certificate (Let's Encrypt)
- Redirect HTTP to HTTPS
- Set HSTS headers

### API Security
```python
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
```

### Environment Secrets
- Never commit `.env` files
- Use platform secrets management
- Rotate keys regularly
- Use different keys per environment

### Rate Limiting
```python
# Add rate limiting middleware
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## 📈 Scaling Strategy

### Horizontal Scaling
1. Use load balancer (AWS ELB, Nginx)
2. Deploy multiple instances
3. Share index via network mount or cache

### Vertical Scaling
1. Increase CPU/RAM allocation
2. Optimize search parameters
3. Add caching layer

### Caching Layer
```bash
# Add Redis for caching
docker run -d -p 6379:6379 redis:latest

# Configure in app
REDIS_URL=redis://localhost:6379
```

---

## 🧪 Testing Production Deployment

### Smoke Test
```bash
curl -X POST "http://your-domain/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Data Scientist",
    "skills": "Python, ML, Statistics"
  }'
```

### Load Test
```bash
# Using Apache Bench
ab -n 100 -c 10 -p request.json \
   -T application/json \
   http://your-domain/recommend

# Or using locust
locust -f locustfile.py
```

### Performance Monitoring
- API response times
- Index loading times
- Memory usage
- CPU usage
- Error rates

---

## 🚨 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs container-name

# Check if port is in use
lsof -i :8000

# Try different port
docker run -p 8001:8000 shl-recommender
```

### High Memory Usage
- Increase container limits
- Reduce CANDIDATE_POOL
- Enable response caching

### Slow Performance
- Check index integrity
- Monitor network I/O
- Profile with cProfile
- Consider adding caching

---

## 📚 Additional Resources

- Docker: https://docs.docker.com/
- Railway: https://docs.railway.app/
- Heroku: https://devcenter.heroku.com/
- AWS EC2: https://docs.aws.amazon.com/ec2/
- Google Cloud Run: https://cloud.google.com/run/docs

---

**Ready to deploy?** Choose your platform above and follow the steps!
