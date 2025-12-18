from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from shlrec.recommender import Recommender
from shlrec.settings import get_settings

app = FastAPI(title="SHL Assessment Recommendation API")

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

@app.get("/health")
def health():
    # Required by assignment: return {"status":"healthy"}
    global _index_error
    if _index_error:
        return {"status": "healthy", "warning": f"Index not loaded: {_index_error}"}
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

_recommender = None
_index_error = None

def get_recommender() -> Recommender:
    global _recommender, _index_error
    if _recommender is None:
        try:
            s = get_settings()
            _recommender = Recommender(index_dir=s.index_dir)
        except Exception as e:
            _index_error = str(e)
            raise

@app.post("/recommend")
def recommend(req: RecommendRequest):
    rec = get_recommender()
    items = rec.recommend(req.query, k=10)
    # Ensure response schema matches assignment exactly
    return {"recommended_assessments": items}
