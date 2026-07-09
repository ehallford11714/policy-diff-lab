"""Optional Streamlit UI for PolicyDiff Lab."""

from __future__ import annotations

import streamlit as st

from policydiff.pipeline import run_policydiff

st.set_page_config(page_title="PolicyDiff Lab", layout="wide")
st.title("PolicyDiff Lab")
st.caption("DiD / event-study workbench for policy & product launches")

c1, c2, c3 = st.columns(3)
n_units = c1.number_input("Units", 10, 200, 40)
t_pre = c2.number_input("Pre periods", 2, 20, 5)
t_post = c3.number_input("Post periods", 2, 20, 5)
true_att = st.slider("True ATT (DGP)", 0.0, 5.0, 2.0, 0.1)
seed = st.number_input("Seed", 0, 9999, 0)

if st.button("Run DiD", type="primary"):
    result = run_policydiff(
        n_units=int(n_units),
        t_pre=int(t_pre),
        t_post=int(t_post),
        true_att=float(true_att),
        seed=int(seed),
    )
    st.metric("ATT", f"{result.did.att:.4f}", help=f"backend={result.did.backend}")
    st.metric("Pre-trend pass", str(result.pre_trends.pass_check))
    st.markdown(result.report_md)
