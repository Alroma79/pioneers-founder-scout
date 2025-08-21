from typing import List, Dict, Any
import os
import pandas as pd

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, "candidates.csv")

REQUIRED = ["name","profile_type","summary","contacts","source_links","match_justification","tier","score"]

def save_candidates_csv(items: List[Dict[str, Any]]) -> str:
    rows = []
    for c in items:
        row = {k: c.get(k) for k in REQUIRED}
        row["contacts"] = ";".join(c.get("contacts") or [])
        row["source_links"] = ";".join(c.get("source_links") or [])
        rows.append(row)
    df = pd.DataFrame(rows)
    if not df.empty:
        df.sort_values(by=["tier","score"], ascending=[True, False], inplace=True)
    df.to_csv(CSV_PATH, index=False)
    return CSV_PATH
