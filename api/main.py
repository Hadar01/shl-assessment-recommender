from fastapi import FastAPI
from pydantic import BaseModel
import os
import traceback
from pathlib import Path
import logging
import pickle
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0.0"
)

# Global data - loaded once
_bm25 = None
_meta = None
_load_error = None

@app.get("/")
def root():
    return {
        "message": "SHL Assessment Recommender API",
        "status": "online"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "data_loaded": _bm25 is not None}

def load_data():
    """Load BM25 and metadata on first need"""
    global _bm25, _meta, _load_error
    
    if _bm25 is not None:
        return True
    
    if _load_error:
        return False
    
    try:
        logger.info("[LOAD] Loading BM25 and metadata...")
        
        # Use settings to get index dir
        from shlrec.settings import get_settings
        settings = get_settings()
        index_dir = Path(settings.index_dir)
        
        # Load BM25
        with open(index_dir / "bm25.pkl", "rb") as f:
            _bm25 = pickle.load(f)
        
        # Load meta
        with open(index_dir / "meta.json", "r", encoding="utf-8") as f:
            _meta = json.load(f)
        
        logger.info(f"[LOAD] SUCCESS: Loaded {len(_meta)} assessments")
        return True
        
    except Exception as e:
        logger.error(f"[LOAD] ERROR: {e}")
        logger.error(traceback.format_exc())
        _load_error = str(e)
        return False

class RecommendRequest(BaseModel):
    query: str

@app.post("/recommend")
def recommend(req: RecommendRequest):
    """Recommendation endpoint"""
    logger.info(f"[REQUEST] {req.query[:60]}")
    
    try:
        # Load if needed
        if not load_data():
            logger.warning("[FALLBACK] Data not loaded")
            return get_mocks()
        
        # BM25 search
        query_tokens = req.query.lower().split()
        scores = _bm25.get_scores(query_tokens)
        
        # Get top 10
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
        results = [_meta[i] for i in top_idx if i < len(_meta)]
        
        if results:
            logger.info(f"[RESULT] {len(results)} assessments")
            return {"recommended_assessments": results}
        else:
            return get_mocks()
        
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return get_mocks()

def get_mocks():
    """Fallback mock data"""
    return {
        "recommended_assessments": [
            {
                "name": "Placeholder - Real Data Unavailable",
                "url": "https://www.shl.com",
                "description": "Using mock data",
                "duration": 0,
                "test_type": [],
                "adaptive_support": "No",
                "remote_support": "Yes"
            }
        ]
    }





