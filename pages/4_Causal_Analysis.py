import streamlit as st

st.title("Causal Analysis")
st.caption("Causal estimands and identification")
st.warning("DML and causal forest estimators are not implemented. No ATE or CATE is available.")
st.markdown("Before estimation, define treatment, index date, outcome horizon, pre-treatment covariates, overlap diagnostics and identification assumptions.")
