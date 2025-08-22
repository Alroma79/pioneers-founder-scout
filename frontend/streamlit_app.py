import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Founder Scout", layout="wide")
st.title("Founder Scout")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
csv_path = os.path.join(BASE_DIR, "data", "candidates.csv")
st.caption(f"Reading: {csv_path}")

if st.button("🔄 Refresh data"):
    st.rerun()

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    for col in ["contacts","source_links","match_justification","summary"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    if set(["tier","score"]).issubset(df.columns):
        df = df.sort_values(["tier","score"], ascending=[True, False])

    st.dataframe(df, use_container_width=True)
else:
    st.info("No candidates.csv found. Run the backend /search.")
