import os
import json
import pickle
from pathlib import Path
import requests
import streamlit as st

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("SHL Assessment Recommendation Demo")

api_url = os.getenv("API_URL", "").strip()

# Debug: Show API_URL status
if api_url:
    st.info(f"✅ API_URL configured: {api_url}")
else:
    st.info("🔍 Using local BM25 search (no API needed)")

query = st.text_area("Enter hiring query or JD URL", height=160, placeholder="e.g., Need a Java developer with stakeholder communication skills. Time limit 40 minutes.")

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

if st.button("Recommend"):
    if not query.strip():
        st.warning("Please enter a query or URL.")
        st.stop()

    try:
        if api_url:
            # Call deployed API
            resp = requests.post(api_url.rstrip("/") + "/recommend", json={"query": query}, timeout=60)
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
            query_tokens = query.lower().split()
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
