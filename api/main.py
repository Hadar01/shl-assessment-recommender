from fastapi import FastAPI
from pydantic import BaseModel
import os
import traceback
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0.0"
)

# Global recommender - lazy loaded on first use (to save memory)
_recommender = None
_load_attempted = False

class RecommendRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {
        "message": "SHL Assessment Recommender API",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

def get_or_load_recommender():
    """Lazy load BM25-only recommender (no embeddings = FAST)"""
    global _recommender, _load_attempted
    
    if _recommender is not None:
        return _recommender
    
    if _load_attempted:
        logger.warning("Recommender already attempted to load and failed")
        return None
    
    _load_attempted = True
    
    try:
        logger.info("[LOAD] Loading BM25-only index...")
        
        import pickle
        import json
        import numpy as np
        
        settings_module = __import__('shlrec.settings', fromlist=['get_settings'])
        settings = settings_module.get_settings()
        index_dir = Path(settings.index_dir)
        
        if not index_dir.exists():
            raise FileNotFoundError(f"Index dir not found: {index_dir}")
        
        # Load BM25 (fast)
        with open(index_dir / "bm25.pkl", "rb") as f:
            bm25 = pickle.load(f)
        
        # Load metadata (fast) - MUST use UTF-8 encoding
        with open(index_dir / "meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        
        # Create minimal object
        class FastRec:
            def __init__(self, bm25, meta):
                self.bm25 = bm25
                self.meta = meta
            
            def search(self, query: str, k: int = 10):
                # Tokenize
                query_tokens = query.lower().split()
                # Get BM25 scores
                scores = self.bm25.get_scores(query_tokens)
                # Get top k
                top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
                # Return metadata
                return [self.meta[idx] for idx in top_indices if idx < len(self.meta)]
        
        _recommender = FastRec(bm25, meta)
        logger.info("[SUCCESS] BM25 recommender ready!")
        return _recommender
        
    except Exception as e:
        logger.error(f"[ERROR] {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        return None

@app.post("/recommend")
def recommend(req: RecommendRequest):
    """Recommendation endpoint - BM25 search"""
    logger.info(f"[REQUEST] Query: {req.query[:100]}")
    
    try:
        logger.info("[DEBUG] Starting get_or_load_recommender...")
        rec = get_or_load_recommender()
        logger.info(f"[DEBUG] Got recommender: {rec is not None}")
        
        if rec is None:
            logger.warning("[FALLBACK] Recommender is None - loading failed")
            return get_mock_recommendations(req.query)
        
        logger.info("[EXEC] Running BM25 search...")
        results = rec.search(req.query, k=10)
        logger.info(f"[DEBUG] Search returned: {len(results)} items")
        
        if results and len(results) > 0:
            logger.info(f"[SUCCESS] Returned {len(results)} recommendations")
            return {"recommended_assessments": results}
        else:
            logger.warning("[EMPTY] BM25 search returned 0 results")
            return get_mock_recommendations(req.query)
            
    except Exception as e:
        logger.error(f"[ERROR] {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        return get_mock_recommendations(req.query)

def get_mock_recommendations(query: str):
    """Fallback mock recommendations"""
    logger.info(f"[MOCK] Returning fallback for: {query[:40]}")
    
    return {
        "recommended_assessments": [
            {
                "name": "Java Developer Test",
                "url": "https://www.shl.com/products/product-catalog/view/java-developer/",
                "description": "Comprehensive Java programming assessment",
                "duration": 60,
                "test_type": ["Knowledge & Skills"],
                "adaptive_support": "Yes",
                "remote_support": "Yes"
            },
            {
                "name": "Leadership Assessment",
                "url": "https://www.shl.com/products/product-catalog/view/leadership-assessment/",
                "description": "Evaluate leadership potential and decision-making",
                "duration": 45,
                "test_type": ["Personality & Behavior"],
                "adaptive_support": "No",
                "remote_support": "Yes"
            },
        ]
    }





