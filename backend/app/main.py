from fastapi import FastAPI
from .models import Criteria

app = FastAPI()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/search")
async def search(criteria: Criteria):
    return {"message": "Stubbed search", "criteria": criteria.dict()}
