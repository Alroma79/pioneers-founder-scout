import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Founder Scout", layout="wide")
st.title("🎯 Founder Scout")

# Custom CSS for tier highlighting
st.markdown("""
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
""", unsafe_allow_html=True)

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

# Summary statistics
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Candidates", len(df))
    with col2:
        tier_a_count = len(df[df.get('tier', '') == 'A'])
        st.metric("Tier A", tier_a_count)
    with col3:
        avg_score = df.get('score', pd.Series([0])).mean()
        st.metric("Avg Score", f"{avg_score:.1f}")
    with col4:
        top_score = df.get('score', pd.Series([0])).max()
        st.metric("Top Score", int(top_score))

# Fill NaNs for display
for col in ["name", "profile_type", "summary", "contacts", "source_links", "match_justification", "tier", "score"]:
    if col in df.columns:
        df[col] = df[col].fillna("")

# Ensure Arrow-friendly numeric score
if "score" in df.columns:
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)

# ---- Sidebar filters (reset BEFORE widget creation) ----
with st.sidebar:
    st.header("Filters")

    tiers_all = sorted([t for t in df.get("tier", pd.Series()).unique() if isinstance(t, str) and t != ""])
    types_all = sorted([t for t in df.get("profile_type", pd.Series()).unique() if isinstance(t, str) and t != ""])

    # One-click reset: set defaults, then rerun BEFORE widgets are rendered
    if st.button("Reset filters"):
        st.session_state["sel_tiers"] = tiers_all
        st.session_state["sel_types"] = types_all
        st.session_state["text_q"] = ""
        st.rerun()

    # Only pass defaults if the keys are not in session_state yet
    if "sel_tiers" not in st.session_state:
        st.session_state["sel_tiers"] = tiers_all
    if "sel_types" not in st.session_state:
        st.session_state["sel_types"] = types_all
    if "text_q" not in st.session_state:
        st.session_state["text_q"] = ""

    sel_tiers = st.multiselect(
        "Tier",
        options=tiers_all,
        default=None if "sel_tiers" in st.session_state else tiers_all,
        key="sel_tiers",
    )
    sel_types = st.multiselect(
        "Profile type",
        options=types_all,
        default=None if "sel_types" in st.session_state else types_all,
        key="sel_types",
    )
    text_q = st.text_input(
        "Text search (name/summary/justification)",
        value=st.session_state.get("text_q", ""),
        key="text_q",
    ).strip().lower()

# ---- Apply filters ----
fdf = df.copy()

# Normalise key columns early
if "tier" in fdf.columns:
    fdf["tier"] = (
        fdf["tier"].astype(str).str.strip().str.upper().replace({"NONE": ""})
    )
if "score" in fdf.columns:
    fdf["score"] = pd.to_numeric(fdf["score"], errors="coerce").fillna(0).astype(int)

# Filters
if "tier" in fdf.columns and st.session_state.get("sel_tiers"):
    fdf = fdf[fdf["tier"].isin(st.session_state["sel_tiers"])]

if "profile_type" in fdf.columns and st.session_state.get("sel_types"):
    fdf = fdf[fdf["profile_type"].isin(st.session_state["sel_types"])]

text_q_val = st.session_state.get("text_q", "").strip().lower()
if text_q_val:
    hay = (
        fdf["name"].astype(str) + " " +
        fdf["summary"].astype(str) + " " +
        fdf["match_justification"].astype(str)
    ).str.lower()
    fdf = fdf[hay.str.contains(text_q_val, na=False)]

# Deterministic sort: A<B<C<other, then score desc, then name asc
tier_order = {"A": 1, "B": 2, "C": 3}
fdf["tier_rank"] = fdf["tier"].map(tier_order).fillna(9).astype(int)
if "name" not in fdf.columns:
    fdf["name"] = ""  # safety

fdf = fdf.sort_values(
    by=["tier_rank", "score", "name"],
    ascending=[True, False, True],
    kind="mergesort",
).drop(columns=["tier_rank"], errors="ignore")

# Human-friendly numbering AFTER sorting (so it’s always 1..N, in order)
numbered = fdf.reset_index(drop=True)
numbered.insert(0, "No.", numbered.index + 1)

# Download filtered CSV with the same numbering & order
st.download_button(
    label="⬇️ Download filtered CSV",
    data=numbered.to_csv(index=False).encode("utf-8"),
    file_name="candidates_filtered.csv",
    mime="text/csv",
)

# Display with numbering and tier highlighting
st.subheader(f"📋 Candidates ({len(numbered)} found)")

# Highlight Tier A candidates
tier_a_candidates = numbered[numbered.get('tier', '') == 'A']
if not tier_a_candidates.empty:
    st.markdown("### ⭐ Tier A Candidates")
    for _, candidate in tier_a_candidates.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="tier-a-highlight">
                <strong>#{candidate.get('No.', 'N/A')} {candidate.get('name', 'N/A')}</strong>
                (Score: {candidate.get('score', 0)}) - {candidate.get('profile_type', 'N/A')}
                <br><small>{candidate.get('summary', 'N/A')}</small>
            </div>
            """, unsafe_allow_html=True)

st.markdown("### 📊 All Candidates")
st.dataframe(numbered, use_container_width=True)
