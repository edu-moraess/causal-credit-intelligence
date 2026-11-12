"""Streamlit entry point. The interface is intentionally read-only at foundation stage."""
import streamlit as st

st.set_page_config(page_title="CCI | ArqTech Labs", page_icon="◈", layout="wide")
st.title("Causal Credit Intelligence")
st.caption("ArqTech Labs · Research platform · Foundation recovery")
st.info("Foundation stage: no dataset has been approved, no model has been trained and no causal effect has been estimated.")
left, right = st.columns(2)
with left:
    st.subheader("Research objective")
    st.write("Investigate the effect of a well-defined credit-limit intervention on subsequent default outcomes, under explicit identification assumptions.")
with right:
    st.subheader("Current gate")
    st.write("Data Engine audit must pass before feature engineering, model fitting or causal estimation.")
st.subheader("Research safeguards")
st.markdown("- Predictive PD is not a causal effect.\n- Covariates must be measured before treatment.\n- Overlap, confounding and temporal ordering must be examined.\n- No automatic download, training or scenario simulation.")
