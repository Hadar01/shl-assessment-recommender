#!/bin/bash
# Run Streamlit on the port specified by Render
streamlit run ui/streamlit_app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --logger.level=info
