import logging
from fastapi import FastAPI, HTTPException
from .models import Criteria
from .clients.harvest_client import HarvestClient
from .services.normalize import normalize_person
from .services.scoring import score_candidate
from .services.utils import dedupe              # NEW: for de-duplication
from .storage.repository import save_candidates_csv

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pioneers Founder Scout")

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Rotation config (tweak freely) ---
ROTATION_QUERIES = [
    "founder ai",
    "founder data",
    "cofounder machine learning",
    "cto ai",
    "founder fintech",
]
TARGET_RESULTS = 40  # stop after we reach this many unique candidates


@app.post("/search")
async def search(criteria: Criteria):
    """
    Flow:
      1) Build title keywords from criteria.
      2) Try Harvest with geoId (if resolvable), then global, then relaxed terms.
      3) Rotate through broader queries until TARGET_RESULTS is reached.
      4) Dedupe -> normalize -> score -> save CSV.
    """
    try:
        harvest = HarvestClient()

        # Build title keywords
        title_parts = []
        if criteria.technical_signal:
            title_parts += ["CTO", "Engineer", "ML", "AI", "Data"]
        if criteria.founder_signal:
            title_parts += ["Founder", "Co-founder"]
        title = ", ".join(sorted(set(title_parts)))

        # Resolve sector (e.g., "Lisbon"/"Portugal"/"Europe") to a geoId
        geo_id = ""
        if criteria.sector and criteria.sector.strip():
            geo_id = await harvest.lookup_geo_id(criteria.sector.strip())

        # Initial attempts (geoId → global → relaxed founder → founder fintech)
        attempts = [
            dict(label="geoId",            search="",                title=title, geo_id=geo_id, location="", page=1, limit=30),
            dict(label="global",           search="",                title=title, geo_id="",     location="", page=1, limit=30),
            dict(label="relaxed-founder",  search="founder",         title="",    geo_id="",     location="", page=1, limit=30),
            dict(label="founder-fintech",  search="founder fintech", title="",    geo_id="",     location="", page=1, limit=30),
        ]

        allowed = {"search", "title", "geo_id", "location", "page", "limit"}
        combined_raw = []
        used_attempt = None

        # Step A: run initial attempts
        for a in attempts:
            logger.info(f"Harvest attempt: {a['label']}", extra={
                'search': a['search'], 'title': a['title'], 'geo_id': a['geo_id']
            })
            kwargs = {k: v for k, v in a.items() if k in allowed}
            try:
                raw = await harvest.search_people(**kwargs)
                logger.info(f"Harvest attempt {a['label']} returned {len(raw)} results")
            except Exception as e:
                logger.error(f"Harvest attempt {a['label']} failed", extra={
                    'error': str(e), 'params': kwargs
                })
                raw = []

            if raw and used_attempt is None:
                used_attempt = a["label"]

            combined_raw.extend(raw)
            combined_raw = dedupe(combined_raw)

            if len(combined_raw) >= TARGET_RESULTS:
                logger.info(f"Target reached with {len(combined_raw)} candidates")

            combined_raw.extend(raw)
            combined_raw = dedupe(combined_raw)

            if len(combined_raw) >= TARGET_RESULTS:
                break

        # Step B: rotate broader queries until target reached
        for q in ROTATION_QUERIES:
            if len(combined_raw) >= TARGET_RESULTS:
                break
            logger.info(f"Harvest rotation query: '{q}'")
            try:
                raw = await harvest.search_people(search=q, title="", geo_id="", location="", page=1, limit=30)
                logger.info(f"Rotation query '{q}' returned {len(raw)} results")
            except Exception as e:
                logger.error(f"Rotation query '{q}' failed", extra={'error': str(e)})
                raw = []

            combined_raw.extend(raw)
            combined_raw = dedupe(combined_raw)

        # Handle case where no results found
        if not combined_raw:
            logger.warning("No candidates found from any source")
            return {
                "count": 0,
                "csv_path": None,
                "items": [],
                "geo_id_used": geo_id or None,
                "attempt_used": used_attempt,
                "rotations_used": ROTATION_QUERIES,
                "message": "No candidates found. Try different search criteria."
            }

        # Normalize, score, save
        logger.info(f"Processing {len(combined_raw)} candidates")
        normalized = [normalize_person(p) for p in combined_raw]
        scored = [score_candidate(p, criteria.model_dump()) for p in normalized]
        csv_path = save_candidates_csv(scored)

        logger.info(f"Saved {len(scored)} candidates to {csv_path}")

        return {
            "count": len(scored),
            "csv_path": csv_path,
            "items": scored[:25],           # preview
            "geo_id_used": geo_id or None,
            "attempt_used": used_attempt,   # which initial attempt returned first
            "rotations_used": ROTATION_QUERIES,
        }

    except Exception as e:
        logger.error(f"Search failed", extra={'error': str(e), 'criteria': criteria.model_dump()})
        raise HTTPException(status_code=500, detail=f"/search failed: {repr(e)}")
