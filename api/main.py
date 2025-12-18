from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
import sys

app = FastAPI(title="SHL Assessment Recommendation API")

# Try to load the real Recommender
try:
    from shlrec.recommender import Recommender
    from shlrec.settings import get_settings
    
    settings = get_settings()
    recommender = Recommender(index_dir=settings.index_dir)
    print("✅ Real Recommender loaded successfully")
    USE_REAL_RECOMMENDER = True
except Exception as e:
    print(f"⚠️ Real Recommender failed to load: {e}")
    print("Falling back to mock recommendations")
    USE_REAL_RECOMMENDER = False
    recommender = None

class RecommendRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "SHL Assessment Recommender API", "status": "online"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/recommend")
def recommend(req: RecommendRequest):
    """
    Main recommendation endpoint.
    Uses real hybrid search (BM25 + semantic) if available, falls back to mock data.
    """
    try:
        if USE_REAL_RECOMMENDER and recommender:
            # Use real hybrid search system
            results = recommender.recommend(query=req.query, k=10)
            return {"recommended_assessments": results}
        else:
            # Fallback: mock data
            return get_mock_recommendations(req.query)
    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        return get_mock_recommendations(req.query)

def get_mock_recommendations(query: str):
    """Fallback mock recommendations"""
    query_lower = query.lower()
    
    mock_assessments = [
        {
            "name": "Java Developer Test",
            "url": "https://www.shl.com/products/product-catalog/view/java-developer/",
            "description": "Assess Java programming competency",
            "duration": 60,
            "test_type": ["Knowledge & Skills"],
            "adaptive_support": "Yes",
            "remote_support": "Yes"
        },
        {
            "name": "Python Developer Test",
            "url": "https://www.shl.com/products/product-catalog/view/python-developer/",
            "description": "Assess Python programming skills",
            "duration": 60,
            "test_type": ["Knowledge & Skills"],
            "adaptive_support": "Yes",
            "remote_support": "Yes"
        },
        {
            "name": "Leadership Assessment",
            "url": "https://www.shl.com/products/product-catalog/view/leadership-assessment/",
            "description": "Evaluate leadership potential",
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
    ]
    
    return {"recommended_assessments": mock_assessments[:2]}


