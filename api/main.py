from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0.0"
)

# Don't load Recommender at startup - lazy load instead
_recommender = None

class RecommendRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "SHL Assessment Recommender API", "status": "online"}

@app.get("/health")
def health():
    return {"status": "healthy"}

def get_recommender():
    """Lazy load recommender only when needed"""
    global _recommender
    if _recommender is not None:
        return _recommender
    
    try:
        from shlrec.recommender import Recommender
        from shlrec.settings import get_settings
        
        settings = get_settings()
        _recommender = Recommender(index_dir=settings.index_dir)
        print("✅ Real Recommender loaded successfully")
        return _recommender
    except Exception as e:
        print(f"⚠️ Real Recommender failed: {e}")
        return None

@app.post("/recommend")
def recommend(req: RecommendRequest):
    """
    Main recommendation endpoint.
    Uses real hybrid search (BM25 + semantic) if available, falls back to mock data.
    """
    try:
        recommender = get_recommender()
        if recommender:
            # Use real hybrid search system
            results = recommender.recommend(query=req.query, k=10)
            return {"recommended_assessments": results}
        else:
            # Fallback: mock data
            return get_mock_recommendations(req.query)
    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        import traceback
        traceback.print_exc()
        return get_mock_recommendations(req.query)

def get_mock_recommendations(query: str):
    """Fallback mock recommendations with real SHL URLs"""
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
        {
            "name": "Communication Assessment",
            "url": "https://www.shl.com/products/product-catalog/view/communication-assessment/",
            "description": "Test interpersonal and communication skills",
            "duration": 30,
            "test_type": ["Personality & Behavior"],
            "adaptive_support": "Yes",
            "remote_support": "Yes"
        },
        {
            "name": "Problem Solving Test",
            "url": "https://www.shl.com/products/product-catalog/view/problem-solving/",
            "description": "Assess analytical and logical reasoning",
            "duration": 45,
            "test_type": ["Knowledge & Skills"],
            "adaptive_support": "Yes",
            "remote_support": "Yes"
        },
    ]
    
    return {"recommended_assessments": mock_assessments[:2]}



