from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import google.generativeai as genai

app = FastAPI(title="SHL Assessment Recommendation API")

# Initialize Gemini if API key available
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

class RecommendRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "SHL Assessment Recommender API", "status": "online"}

@app.get("/health")
def health():
    return {"status": "healthy"}

def extract_intent_with_llm(query: str) -> dict:
    """Use Gemini to extract hiring intent from query"""
    if not GEMINI_KEY:
        return {"skills": [], "roles": [], "seniority": "mid", "domain": "K"}
    
    prompt = f"""Extract hiring requirements from this query. Return ONLY valid JSON:
{{
  "hard_skills": [list of technical skills needed],
  "soft_skills": [list of soft skills like leadership, communication],
  "roles": [job roles],
  "seniority": "intern|junior|mid|senior|lead",
  "domain": "K" for technical, "P" for people/soft skills, "B" for balanced
}}

QUERY: {query}

Return ONLY the JSON object, no markdown."""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        intent = json.loads(response.text)
        return intent
    except Exception as e:
        print(f"LLM error: {e}")
        return {"skills": [], "roles": [], "seniority": "mid", "domain": "K"}

@app.post("/recommend")
def recommend(req: RecommendRequest):
    # Parse intent using LLM
    intent = extract_intent_with_llm(req.query)
    
    # Assessment database - more comprehensive
    assessments_db = {
        "technical": [
            {"name": "Java Developer Test", "url": "https://shl.com/java", "description": "Test Java programming skills", "duration": 60, "test_type": "K", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["java", "programming"]},
            {"name": "Python Developer Test", "url": "https://shl.com/python", "description": "Test Python programming skills", "duration": 60, "test_type": "K", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["python", "programming"]},
            {"name": "Problem Solving Test", "url": "https://shl.com/problem-solving", "description": "Test analytical and problem-solving skills", "duration": 45, "test_type": "K", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["problem solving", "analytical"]},
            {"name": "Data Analysis Test", "url": "https://shl.com/data-analysis", "description": "Test data analysis and SQL skills", "duration": 50, "test_type": "K", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["data", "sql", "analysis"]},
            {"name": "Full Stack Developer Test", "url": "https://shl.com/fullstack", "description": "Test full-stack web development skills", "duration": 75, "test_type": "K", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["javascript", "react", "nodejs", "web"]},
        ],
        "soft_skills": [
            {"name": "Leadership Assessment", "url": "https://shl.com/leadership", "description": "Test leadership potential and decision-making", "duration": 45, "test_type": "P", "adaptive_support": "No", "remote_support": "Yes", "skills": ["leadership", "management", "decision making"]},
            {"name": "Communication Assessment", "url": "https://shl.com/communication", "description": "Test communication and interpersonal skills", "duration": 30, "test_type": "P", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["communication", "collaboration", "teamwork", "stakeholder"]},
            {"name": "Management Aptitude Test", "url": "https://shl.com/management", "description": "Test management and organizational skills", "duration": 50, "test_type": "P", "adaptive_support": "No", "remote_support": "Yes", "skills": ["management", "organization", "delegation"]},
            {"name": "Emotional Intelligence Test", "url": "https://shl.com/ei", "description": "Test emotional intelligence and interpersonal awareness", "duration": 25, "test_type": "P", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["emotional intelligence", "awareness", "empathy"]},
        ],
        "balanced": [
            {"name": "Technician Assessment", "url": "https://shl.com/technician", "description": "Test technical skills + problem-solving + teamwork", "duration": 60, "test_type": "B", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["technical", "collaboration", "problem solving"]},
            {"name": "Engineering Manager Test", "url": "https://shl.com/eng-manager", "description": "Test technical knowledge + leadership", "duration": 75, "test_type": "B", "adaptive_support": "Yes", "remote_support": "Yes", "skills": ["technical", "leadership", "management"]},
        ]
    }
    
    # Select assessments based on intent
    recommended = []
    domain = intent.get("domain", "K")
    
    if domain == "K":
        # Technical focus
        recommended.extend(assessments_db["technical"][:2])
    elif domain == "P":
        # People/soft skills focus
        recommended.extend(assessments_db["soft_skills"][:2])
    else:  # Balanced
        recommended.append(assessments_db["balanced"][0])
        recommended.extend(assessments_db["soft_skills"][:1])
    
    # Match based on extracted skills
    hard_skills = intent.get("hard_skills", [])
    soft_skills = intent.get("soft_skills", [])
    
    # Add skill-specific assessments
    for skill in hard_skills:
        for assessment in assessments_db["technical"]:
            if any(s in skill.lower() for s in assessment["skills"]) and assessment not in recommended:
                recommended.append(assessment)
                if len(recommended) >= 3:
                    break
    
    for skill in soft_skills:
        for assessment in assessments_db["soft_skills"]:
            if any(s in skill.lower() for s in assessment["skills"]) and assessment not in recommended:
                recommended.append(assessment)
                if len(recommended) >= 3:
                    break
    
    # Ensure we have at least 2 recommendations
    if len(recommended) < 2:
        recommended = assessments_db["technical"][:1] + assessments_db["soft_skills"][:1]
    
    # Limit to 3
    recommended = recommended[:3]
    
    return {"recommended_assessments": recommended}

