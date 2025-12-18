from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="SHL Assessment Recommendation API")

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
    return {
        "recommended_assessments": [
            {
                "name": "Java Developer Test",
                "url": "https://shl.com/java",
                "description": "Test Java skills",
                "duration": 60,
                "test_type": ["K"],
                "adaptive_support": "Yes",
                "remote_support": "Yes"
            },
            {
                "name": "Leadership Assessment",
                "url": "https://shl.com/leadership",
                "description": "Test leadership skills",
                "duration": 45,
                "test_type": ["C"],
                "adaptive_support": "No",
                "remote_support": "Yes"
            }
        ]
    }
