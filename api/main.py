from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="SHL Assessment Recommendation API")

# Global state
_recommender = None
_index_error = None

class RecommendRequest(BaseModel):
    query: str

class AssessmentOut(BaseModel):
    url: str
    adaptive_support: str
    description: str
    duration: int
    name: str
    remote_support: str
    test_type: List[str]

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "SHL Assessment Recommender API", "status": "online"}

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/status")
def status():
    """Check if recommender is ready"""
    global _recommender, _index_error
    if _recommender is not None:
        return {"ready": True, "message": "Recommender loaded"}
    if _index_error:
        return {"ready": False, "message": f"Index error: {_index_error}"}
    return {"ready": False, "message": "Recommender not initialized"}

def get_recommender():
    global _recommender, _index_error
    if _recommender is not None:
        return _recommender
    if _index_error:
        raise Exception(f"Previous error: {_index_error}")
    
    try:
        print("[DEBUG] Loading settings...")
        from shlrec.settings import get_settings
        s = get_settings()
        print(f"[DEBUG] Settings loaded. INDEX_DIR={s.index_dir}")
        
        # Check if index dir exists
        if not os.path.exists(s.index_dir):
            raise FileNotFoundError(f"Index directory not found: {s.index_dir}")
        print(f"[DEBUG] Index directory exists")
        
        print("[DEBUG] Importing Recommender...")
        from shlrec.recommender import Recommender
        print("[DEBUG] Recommender imported successfully")
        
        print("[DEBUG] Initializing Recommender...")
        _recommender = Recommender(index_dir=s.index_dir)
        print("[DEBUG] Recommender initialized successfully")
        
        return _recommender
    except Exception as e:
        _index_error = str(e)
        import traceback
        tb = traceback.format_exc()
        print(f"[ERROR] {tb}")
        raise

@app.post("/recommend")
def recommend(req: RecommendRequest):
    try:
        # MOCK DATA - Temporary working response
        mock_data = [
            {"name": "Java Developer Test", "url": "https://shl.com/java", "description": "Test Java skills", "duration": 60, "test_type": ["K"], "adaptive_support": "Yes", "remote_support": "Yes"},
            {"name": "Leadership Skills", "url": "https://shl.com/leadership", "description": "Test leadership", "duration": 45, "test_type": ["C"], "adaptive_support": "No", "remote_support": "Yes"}
        ]
        return {"recommended_assessments": mock_data}
    except Exception as e:
        return {"error": str(e), "recommended_assessments": []}
