from fastapi import FastAPI
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
    parts = []
    if criteria.sector: parts.append(criteria.sector)
    if criteria.technical_signal: parts.append("CTO OR ML OR AI OR Data")
    if criteria.founder_signal: parts.append("founder OR co-founder")
    query = " ".join(parts) or "founder"

    client = HarvestClient()
    raw = await client.search_people(query=query, limit=30)

    normalized = [normalize_person(p) for p in raw]
    scored = [score_candidate(p, criteria.model_dump()) for p in normalized]
    csv_path = save_candidates_csv(scored)

    return {"count": len(scored), "csv_path": csv_path, "items": scored[:25]}
