import os
import requests
import streamlit as st

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("SHL Assessment Recommendation Demo")

api_url = os.getenv("API_URL", "").strip()

# Debug: Show API_URL status
if api_url:
    st.info(f"✅ API_URL configured: {api_url}")
else:
    st.warning("❌ API_URL not set - will use local import")
query = st.text_area("Enter hiring query or JD URL", height=160, placeholder="e.g., Need a Java developer with stakeholder communication skills. Time limit 40 minutes.")

if st.button("Recommend"):
    if not query.strip():
        st.warning("Please enter a query or URL.")
        st.stop()

    if api_url:
        # Call deployed API
        resp = requests.post(api_url.rstrip("/") + "/recommend", json={"query": query}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        recs = data.get("recommended_assessments", [])
    else:
        # Local import (no server required)
        from shlrec.recommender import Recommender
        from shlrec.settings import get_settings
        s = get_settings()
        recs = Recommender(index_dir=s.index_dir).recommend(query, k=10)

    if not recs:
        st.error("No recommendations returned.")
    else:
        st.success(f"Returned {len(recs)} recommendations")
        st.dataframe(recs, use_container_width=True)
        st.markdown("Tip: set `API_URL` to your deployed API (e.g., `https://your-api.onrender.com`).")
