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
    query_lower = req.query.lower()
    
    # Mock assessment database
    assessments = {
        "java": {
            "name": "Java Developer Test",
            "url": "https://shl.com/java",
            "description": "Test Java skills",
            "duration": 60,
            "test_type": "K",
            "adaptive_support": "Yes",
            "remote_support": "Yes"
        },
        "python": {
            "name": "Python Developer Test",
            "url": "https://shl.com/python",
            "description": "Test Python skills",
            "duration": 60,
            "test_type": "K",
            "adaptive_support": "Yes",
            "remote_support": "Yes"
        },
        "leadership": {
            "name": "Leadership Assessment",
            "url": "https://shl.com/leadership",
            "description": "Test leadership skills",
            "duration": 45,
            "test_type": "C",
            "adaptive_support": "No",
            "remote_support": "Yes"
        },
        "communication": {
            "name": "Communication Assessment",
            "url": "https://shl.com/communication",
            "description": "Test communication skills",
            "duration": 30,
            "test_type": "B",
            "adaptive_support": "Yes",
            "remote_support": "Yes"
        },
        "management": {
            "name": "Management Aptitude Test",
            "url": "https://shl.com/management",
            "description": "Test management potential",
            "duration": 50,
            "test_type": "A",
            "adaptive_support": "No",
            "remote_support": "Yes"
        },
        "problem": {
            "name": "Problem Solving Test",
            "url": "https://shl.com/problem-solving",
            "description": "Test analytical and problem-solving skills",
            "duration": 45,
            "test_type": "K",
            "adaptive_support": "Yes",
            "remote_support": "Yes"
        }
    }
    
    # Find matching assessments based on query keywords
    recommended = []
    for keyword, assessment in assessments.items():
        if keyword in query_lower:
            recommended.append(assessment)
    
    # If no matches, return default recommendations
    if not recommended:
        recommended = [assessments["leadership"], assessments["communication"]]
    
    return {"recommended_assessments": recommended}
