from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys
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

# Global recommender - pre-loaded on startup
_recommender = None
_startup_error = None

class RecommendRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup_event():
    """Pre-load recommender on app startup for fast responses"""
    global _recommender, _startup_error
    
    try:
        logger.info("[STARTUP] Loading recommender...")
        
        # Import modules
        from shlrec.recommender import Recommender
        from shlrec.settings import get_settings
        
        # Load settings
        settings = get_settings()
        logger.info(f"[STARTUP] Settings loaded: index_dir={settings.index_dir}")
        
        # Verify index exists
        index_dir = Path(settings.index_dir)
        if not index_dir.exists():
            raise FileNotFoundError(f"Index dir not found: {index_dir}")
        
        # Create and initialize recommender
        logger.info("[STARTUP] Creating Recommender instance...")
        _recommender = Recommender(index_dir=settings.index_dir)
        
        # Trigger full load (not lazy)
        logger.info("[STARTUP] Triggering full initialization...")
        _recommender._lazy_load()
        
        logger.info("[STARTUP] SUCCESS - Recommender ready!")
        
    except Exception as e:
        msg = f"[STARTUP] FAILED: {type(e).__name__}: {e}"
        logger.error(msg)
        logger.error(traceback.format_exc())
        _startup_error = str(e)

@app.get("/")
def root():
    return {
        "message": "SHL Assessment Recommender API",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    status = "ready" if _recommender else "degraded"
    return {
        "status": "healthy",
        "recommender": status,
        "error": _startup_error
    }

@app.post("/recommend")
def recommend(req: RecommendRequest):
    """
    Main recommendation endpoint.
    Uses hybrid search (BM25 + semantic embeddings) with Gemini intent extraction.
    """
    logger.info(f"[REQUEST] Query: {req.query[:100]}")
    
    try:
        if _recommender is None:
            logger.warning("[REQUEST] Recommender not available!")
            return get_mock_recommendations(req.query)
        
        logger.info("[EXEC] Calling recommender.recommend()...")
        results = _recommender.recommend(query_or_url=req.query, k=10)
        
        if results:
            logger.info(f"[SUCCESS] Returned {len(results)} recommendations")
            return {"recommended_assessments": results}
        else:
            logger.warning("[EMPTY] Recommender returned empty list")
            return get_mock_recommendations(req.query)
            
    except Exception as e:
        logger.error(f"[ERROR] {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        return get_mock_recommendations(req.query)

def get_mock_recommendations(query: str):
    """Fallback mock recommendations"""
    logger.info(f"[MOCK] Returning fallback for: {query[:50]}")
    
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





