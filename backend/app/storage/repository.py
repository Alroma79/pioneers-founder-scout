from typing import List, Dict, Any
import os
import pandas as pd
import shutil
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, "candidates.csv")

REQUIRED = ["name","profile_type","summary","contacts","source_links","match_justification","tier","score"]

def save_candidates_csv(items: List[Dict[str, Any]]) -> str:
    # Create backup if file exists
    if os.path.exists(CSV_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(DATA_DIR, f"candidates_backup_{timestamp}.csv")
        try:
            shutil.copy2(CSV_PATH, backup_path)
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")

    rows = []
    for c in items:
        row = {k: (c.get(k) or "") for k in REQUIRED}
        # stringify lists and ensure no None values
        row["contacts"] = ";".join(str(x) for x in (c.get("contacts") or []) if x)
        row["source_links"] = ";".join(str(x) for x in (c.get("source_links") or []) if x)
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df.sort_values(by=["tier","score"], ascending=[True, False], inplace=True)

    df.to_csv(CSV_PATH, index=False)
    logger.info(f"Saved {len(items)} candidates to {CSV_PATH}")
    return CSV_PATH