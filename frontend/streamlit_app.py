
import os
import pandas as pd
import streamlit as st

# ---------- Page ----------
st.set_page_config(page_title="Founder Scout", layout="wide")
st.title("🎯 Founder Scout")

# ---------- CSS ----------
st.markdown(
    """
<style>
.tier-a-highlight {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
    padding: 10px;
    margin: 5px 0;
}
.summary-card {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- Paths ----------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
csv_path = os.path.join(BASE_DIR, "data", "candidates.csv")
st.caption(f"Reading: {csv_path}")

# ---------- Refresh ----------
if st.button("🔄 Refresh data"):
    st.rerun()

if not os.path.exists(csv_path):
    st.info("No candidates.csv found. Run the backend /search.")
    st.stop()

# ---------- Load ----------
df = pd.read_csv(csv_path)

# Basic cleaning for display / operations
for col in ["name", "profile_type", "summary", "contacts", "source_links", "match_justification", "tier", "score"]:
    if col in df.columns:
        df[col] = df[col].fillna("")

if "score" in df.columns:
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.header("Filters")

    tiers_all = sorted([t for t in df.get("tier", pd.Series()).unique() if isinstance(t, str) and t != ""])
    types_all = sorted([t for t in df.get("profile_type", pd.Series()).unique() if isinstance(t, str) and t != ""])

    # One-click reset
    if st.button("Reset filters"):
        st.session_state["sel_tiers"] = tiers_all
        st.session_state["sel_types"] = types_all
        st.session_state["text_q"] = ""
        st.rerun()

    # Bootstrap session defaults once
    st.session_state.setdefault("sel_tiers", tiers_all)
    st.session_state.setdefault("sel_types", types_all)
    st.session_state.setdefault("text_q", "")

    sel_tiers = st.multiselect("Tier", options=tiers_all, key="sel_tiers")
    sel_types = st.multiselect("Profile type", options=types_all, key="sel_types")
    text_q = st.text_input("Text search (name/summary/justification)", key="text_q").strip().lower()

# ---------- Apply Filters ----------
fdf = df.copy()

# Normalize tier + score defensively
if "tier" in fdf.columns:
    fdf["tier"] = fdf["tier"].astype(str).str.strip().str.upper().replace({"NONE": ""})
if "score" in fdf.columns:
    fdf["score"] = pd.to_numeric(fdf["score"], errors="coerce").fillna(0).astype(int)

# Tier filter
if "tier" in fdf.columns and st.session_state.get("sel_tiers"):
    fdf = fdf[fdf["tier"].isin(st.session_state["sel_tiers"])]

# Profile type filter
if "profile_type" in fdf.columns and st.session_state.get("sel_types"):
    fdf = fdf[fdf["profile_type"].isin(st.session_state["sel_types"])]

# Text filter
text_q_val = st.session_state.get("text_q", "").strip().lower()
if text_q_val:
    hay = (
        fdf.get("name", "").astype(str) + " "
        + fdf.get("summary", "").astype(str) + " "
        + fdf.get("match_justification", "").astype(str)
    ).str.lower()
    fdf = fdf[hay.str.contains(text_q_val, na=False)]

# ---------- Sort: Tier → Score → Name ----------
tier_order = {"A": 1, "B": 2, "C": 3}
fdf["tier_rank"] = fdf["tier"].map(tier_order).fillna(9).astype(int)
if "name" not in fdf.columns:
    fdf["name"] = ""  # safety

fdf = (
    fdf.sort_values(by=["tier_rank", "score", "name"], ascending=[True, False, True], kind="mergesort")
      .drop(columns=["tier_rank"], errors="ignore")
      .reset_index(drop=True)
)

# ---------- Summary Bar (filtered view) ----------
total_count = len(df)
filtered_count = len(fdf)
avg_score = float(fdf["score"].mean()) if "score" in fdf.columns and not fdf.empty else 0.0
top_score = int(fdf["score"].max()) if "score" in fdf.columns and not fdf.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Candidates", total_count)
c2.metric("Filtered", filtered_count)
c3.metric("Avg Score", f"{avg_score:.1f}")
c4.metric("Top Score", top_score)

# ---------- Numbering AFTER sorting (1..N) ----------
numbered = fdf.copy()
if "No." in numbered.columns:
    numbered = numbered.drop(columns=["No."])
numbered.insert(0, "No.", range(1, len(numbered) + 1))

# ---------- Download (use the same view the user sees) ----------
st.download_button(
    label="📥 Download filtered CSV",
    data=numbered.to_csv(index=False).encode("utf-8"),
    file_name="candidates_filtered.csv",
    mime="text/csv",
)

# ---------- Tier A cards ----------
st.subheader(f"📋 Candidates ({len(numbered)} found)")

tier_a_candidates = numbered[numbered.get("tier", "") == "A"]
if not tier_a_candidates.empty:
    st.markdown("### ⭐ Tier A Candidates")
    for _, candidate in tier_a_candidates.iterrows():
        st.markdown(
            f"""
<div class="tier-a-highlight">
  <strong>#{candidate.get('No.', 'N/A')} {candidate.get('name', 'N/A')}</strong>
  (Score: {candidate.get('score', 0)}) — {candidate.get('profile_type', 'N/A')}
  <br><small>{candidate.get('summary', 'N/A')}</small>
</div>
""",
            unsafe_allow_html=True,
        )

# ---------- Full table (index hidden; 1-based shown) ----------
st.markdown("### 📊 All Candidates")
st.dataframe(numbered.set_index("No.").rename_axis(None), use_container_width=True)
