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
    return {"status": "healthy"}

_recommender = None

def get_recommender() -> Recommender:
    global _recommender
    if _recommender is None:
        s = get_settings()
        _recommender = Recommender(index_dir=s.index_dir)
    return _recommender

@app.post("/recommend")
def recommend(req: RecommendRequest):
    rec = get_recommender()
    items = rec.recommend(req.query, k=10)
    # Ensure response schema matches assignment exactly
    return {"recommended_assessments": items}
