import streamlit as st

st.title("Data Explorer")
st.caption("Read-only data inspection · Phase 1")
st.info("No dataset is configured. Place an approved CSV or Parquet file in data/raw/ after reviewing privacy and permissions.")
st.code("python -m pip install -r requirements.txt\nPYTHONPATH=src pytest -q", language="bash")
