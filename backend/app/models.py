from typing import List, Optional, Literal
from pydantic import BaseModel

ProfileType = Literal["business", "technical"]

class Criteria(BaseModel):
    min_years_experience: int = 5
    sector: Optional[str] = None
    academic: Optional[str] = None
    founder_signal: bool = True
    technical_signal: bool = True
    startup_experience_required: bool = True

class Candidate(BaseModel):
    name: str
    profile_type: ProfileType
    summary: str
    contacts: List[str] = []
    source_links: List[str] = []
    match_justification: str
    tier: Literal["A","B","C"] = "C"
    score: int = 0
