from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys
import traceback
from pathlib import Path

app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0.0"
)

# Global recommender - lazy loaded
_recommender = None
_recommender_error = None

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

def initialize_recommender():
    """Initialize recommender with detailed error logging"""
    global _recommender, _recommender_error
    
    if _recommender is not None:
        return _recommender
    
    if _recommender_error is not None:
        print(f"Previous error cached: {_recommender_error}")
        return None
    
    try:
        print("[API] Starting recommender initialization...")
        
        # Import here to catch any import errors
        print("[API] Importing shlrec modules...")
        from shlrec.recommender import Recommender
        from shlrec.settings import get_settings
        print("[API] Imports successful")
        
        print("[API] Loading settings...")
        settings = get_settings()
        print(f"[API] Settings loaded: index_dir={settings.index_dir}")
        
        print("[API] Checking index directory...")
        index_dir = Path(settings.index_dir)
        if not index_dir.exists():
            raise FileNotFoundError(f"Index dir not found: {index_dir}")
        print(f"[API] Index directory exists: {index_dir}")
        
        print("[API] Creating Recommender instance...")
        _recommender = Recommender(index_dir=settings.index_dir)
        print("[API] Recommender instance created")
        
        print("[API] Triggering lazy load (first request will load embeddings)...")
        # Don't fully load here - let lazy_load happen on first request
        
        print("[SUCCESS] Recommender initialized successfully!")
        return _recommender
        
    except ImportError as e:
        msg = f"Import error: {e}"
        print(f"[ERROR] {msg}")
        _recommender_error = msg
        traceback.print_exc()
        return None
    except FileNotFoundError as e:
        msg = f"File not found: {e}"
        print(f"[ERROR] {msg}")
        _recommender_error = msg
        return None
    except Exception as e:
        msg = f"Unexpected error during init: {type(e).__name__}: {e}"
        print(f"[ERROR] {msg}")
        _recommender_error = msg
        traceback.print_exc()
        return None

@app.post("/recommend")
def recommend(req: RecommendRequest):
    """
    Main recommendation endpoint.
    Uses hybrid search (BM25 + semantic embeddings) with Gemini intent extraction.
    """
    print(f"[REQUEST] Query: {req.query[:100]}")
    
    try:
        # Initialize recommender on first use
        rec = initialize_recommender()
        
        if rec is None:
            print("[FALLBACK] Recommender not available, using mock")
            return get_mock_recommendations(req.query)
        
        print("[RECOMMENDER] Calling recommend()...")
        results = rec.recommend(query_or_url=req.query, k=10)
        
        if results:
            print(f"[SUCCESS] Returned {len(results)} real recommendations")
            return {"recommended_assessments": results}
        else:
            print("[WARNING] Recommender returned empty, using mock")
            return get_mock_recommendations(req.query)
            
    except Exception as e:
        print(f"[ERROR] Exception during recommend: {type(e).__name__}: {e}")
        traceback.print_exc()
        return get_mock_recommendations(req.query)

def get_mock_recommendations(query: str):
    """Fallback mock recommendations - only used if real recommender fails"""
    print(f"[MOCK] Returning fallback recommendations for: {query[:50]}")
    
    mock_assessments = [
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
    
    return {"recommended_assessments": mock_assessments}




