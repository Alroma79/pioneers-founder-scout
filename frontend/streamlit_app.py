import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Founder Scout", layout="wide")
st.title("Founder Scout")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
csv_path = os.path.join(BASE_DIR, "data", "candidates.csv")
st.caption(f"Reading: {csv_path}")

# Refresh
if st.button("🔄 Refresh data"):
    st.rerun()

if not os.path.exists(csv_path):
    st.info("No candidates.csv found. Run the backend /search.")
    st.stop()

df = pd.read_csv(csv_path)

# Fill NaNs for display
for col in ["name","profile_type","summary","contacts","source_links","match_justification","tier","score"]:
    if col in df.columns:
        df[col] = df[col].fillna("")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    tiers = sorted([t for t in df.get("tier", pd.Series()).unique() if isinstance(t, str)])
    types = sorted([t for t in df.get("profile_type", pd.Series()).unique() if isinstance(t, str)])

    sel_tiers = st.multiselect("Tier", options=tiers, default=tiers)
    sel_types = st.multiselect("Profile type", options=types, default=types)
    text_q = st.text_input("Text search (name/summary/justification)").strip().lower()

# Apply filters
fdf = df.copy()
if "tier" in fdf.columns and sel_tiers:
    fdf = fdf[fdf["tier"].isin(sel_tiers)]
if "profile_type" in fdf.columns and sel_types:
    fdf = fdf[fdf["profile_type"].isin(sel_types)]
if text_q:
    hay = (fdf["name"].astype(str) + " " + fdf["summary"].astype(str) + " " + fdf["match_justification"].astype(str)).str.lower()
    fdf = fdf[hay.str.contains(text_q, na=False)]

# Sort for readability
if set(["tier","score"]).issubset(fdf.columns):
    fdf = fdf.sort_values(["tier","score"], ascending=[True, False])

# Download filtered CSV
st.download_button(
    label="⬇️ Download filtered CSV",
    data=fdf.to_csv(index=False).encode("utf-8"),
    file_name="candidates_filtered.csv",
    mime="text/csv",
)

st.dataframe(fdf, use_container_width=True)
