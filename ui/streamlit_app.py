import os
import json
import pickle
from pathlib import Path
import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("SHL Assessment Recommendation Demo")

api_url = os.getenv("API_URL", "").strip()

# Debug: Show API_URL status
if api_url:
    st.info(f"✅ API_URL configured: {api_url}")
else:
    st.info("🔍 Using local BM25 search (no API needed)")

query = st.text_area("Enter hiring query or JD URL", height=160, placeholder="e.g., Need a Java developer with stakeholder communication skills. Time limit 40 minutes. Or paste a LinkedIn job URL.")

@st.cache_resource
def load_bm25_index():
    """Load BM25 index and metadata"""
    try:
        index_dir = Path("data/index")
        
        # Load BM25
        with open(index_dir / "bm25.pkl", "rb") as f:
            bm25 = pickle.load(f)
        
        # Load metadata
        with open(index_dir / "meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        
        return bm25, meta
    except Exception as e:
        st.error(f"Failed to load index: {e}")
        return None, None

def is_url(text):
    """Check if text is a URL"""
    return text.strip().startswith(('http://', 'https://'))

def extract_text_from_url(url, timeout=10):
    """Extract text from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:2000] if text else ""
    except Exception as e:
        st.warning(f"Could not extract from URL: {e}")
        return ""

if st.button("Recommend"):
    if not query.strip():
        st.warning("Please enter a query or URL.")
        st.stop()

    search_query = query.strip()
    
    # If input is URL, extract text
    if is_url(search_query):
        st.info("📄 Extracting job description from URL...")
        extracted_text = extract_text_from_url(search_query)
        if extracted_text:
            search_query = extracted_text
            st.success(f"✅ Extracted {len(search_query)} characters from URL")
        else:
            st.warning("Could not extract text from URL, using URL as query")

    try:
        if api_url:
            # Call deployed API
            resp = requests.post(api_url.rstrip("/") + "/recommend", json={"query": search_query}, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            recs = data.get("recommended_assessments", [])
        else:
            # Local BM25 search
            bm25, meta = load_bm25_index()
            if bm25 is None or meta is None:
                st.error("Could not load search index.")
                st.stop()
            
            # BM25 search
            query_tokens = search_query.lower().split()
            scores = bm25.get_scores(query_tokens)
            
            # Get top 10
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
            recs = [meta[i] for i in top_indices if i < len(meta)]

        if not recs:
            st.error("No recommendations returned.")
        else:
            st.success(f"✅ Returned {len(recs)} recommendations")
            st.dataframe(recs, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching recommendations: {str(e)}")
