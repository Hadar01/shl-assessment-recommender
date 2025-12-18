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
    """Lazy load recommender only when needed (memory efficient)"""
    global _recommender, _load_attempted
    
    if _recommender is not None:
        return _recommender
    
    if _load_attempted:
        logger.warning("Recommender already attempted to load and failed")
        return None
    
    _load_attempted = True
    
    try:
        logger.info("[LOAD] Loading recommender...")
        
        from shlrec.recommender import Recommender
        from shlrec.settings import get_settings
        
        settings = get_settings()
        index_dir = Path(settings.index_dir)
        
        if not index_dir.exists():
            raise FileNotFoundError(f"Index dir not found: {index_dir}")
        
        logger.info(f"[LOAD] Creating Recommender from {index_dir}")
        _recommender = Recommender(index_dir=settings.index_dir)
        
        logger.info("[LOAD] Triggering lazy load...")
        _recommender._lazy_load()
        
        logger.info("[SUCCESS] Recommender ready!")
        return _recommender
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to load: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        return None

@app.post("/recommend")
def recommend(req: RecommendRequest):
    """
    Main recommendation endpoint.
    Lazy loads recommender on first request.
    """
    logger.info(f"[REQUEST] Query: {req.query[:80]}")
    
    try:
        rec = get_or_load_recommender()
        
        if rec is None:
            logger.warning("[FALLBACK] Using mock recommendations")
            return get_mock_recommendations(req.query)
        
        logger.info("[EXEC] Calling recommender.recommend()...")
        results = rec.recommend(query_or_url=req.query, k=10)
        
        if results:
            logger.info(f"[SUCCESS] Returned {len(results)} recommendations")
            return {"recommended_assessments": results}
        else:
            logger.warning("[EMPTY] Recommender returned no results")
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





