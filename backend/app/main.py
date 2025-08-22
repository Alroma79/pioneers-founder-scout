from fastapi import FastAPI, HTTPException
from .models import Criteria
from .clients.harvest_client import HarvestClient
from .services.normalize import normalize_person
from .services.scoring import score_candidate
from .storage.repository import save_candidates_csv

app = FastAPI(title="Pioneers Founder Scout")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/search")
async def search(criteria: Criteria):
    """
    Build title keywords. Try Harvest with:
      1) geoId if resolvable from 'sector'
      2) global (no geoId)
      3) relaxed free-text 'founder'
      4) 'founder fintech' (known-good)
    First non-empty result wins.
    """
    try:
        harvest = HarvestClient()

        # title keywords from criteria
        title_parts = []
        if criteria.technical_signal:
            title_parts += ["CTO", "Engineer", "ML", "AI", "Data"]
        if criteria.founder_signal:
            title_parts += ["Founder", "Co-founder"]
        title = ", ".join(sorted(set(title_parts)))

        # Resolve sector (Lisbon/Portugal/Europe) -> geoId
        geo_id = ""
        if criteria.sector and criteria.sector.strip():
            geo_id = await harvest.lookup_geo_id(criteria.sector.strip())

        attempts = [
            dict(label="geoId",
                 search="",
                 title=title,
                 geo_id=geo_id,
                 location="",
                 page=1,
                 limit=30),
            dict(label="global",
                 search="",
                 title=title,
                 geo_id="",
                 location="",
                 page=1,
                 limit=30),
            dict(label="relaxed-founder",
                 search="founder",
                 title="",
                 geo_id="",
                 location="",
                 page=1,
                 limit=30),
            dict(label="founder-fintech",
                 search="founder fintech",
                 title="",
                 geo_id="",
                 location="",
                 page=1,
                 limit=30),
        ]

        # ... keep the rest of the file as you have it ...

        all_raw = []
        used_attempt = None

        # Only these keys are valid for HarvestClient.search_people
        allowed = {"search", "title", "geo_id", "location", "page", "limit"}

        for a in attempts:
            print(f"[Harvest Attempt] {a['label']} -> search='{a['search']}', title='{a['title']}', geoId='{a['geo_id']}'")
            kwargs = {k: v for k, v in a.items() if k in allowed}
            try:
                raw = await harvest.search_people(**kwargs)
                print(f"[Harvest Attempt] {a['label']} -> returned {len(raw)} results")
            except Exception as e:
                print(f"[Harvest Attempt] {a['label']} -> ERROR: {repr(e)}")
                raw = []

            if raw:
                all_raw = raw
                used_attempt = a["label"]
                break


        normalized = [normalize_person(p) for p in all_raw]
        scored = [score_candidate(p, criteria.model_dump()) for p in normalized]
        csv_path = save_candidates_csv(scored)

        return {
            "count": len(scored),
            "csv_path": csv_path,
            "items": scored[:25],
            "geo_id_used": geo_id or None,
            "attempt_used": used_attempt,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/search failed: {repr(e)}")
