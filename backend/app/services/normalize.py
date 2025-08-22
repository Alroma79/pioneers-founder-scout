from typing import Dict, Any

def normalize_person(raw: Dict[str, Any]) -> Dict[str, Any]:
    name       = raw.get("name") or raw.get("publicIdentifier") or "LinkedIn Member"
    headline   = raw.get("position") or ""
    linkedin   = raw.get("linkedinUrl") or ""
    public_id  = raw.get("publicIdentifier") or ""
    loc_obj    = raw.get("location") or {}
    location   = loc_obj.get("linkedinText") or ""

    # Build a URL if linkedinUrl missing but publicIdentifier present
    if not linkedin and public_id:
        linkedin = f"https://www.linkedin.com/in/{public_id}"

    profile_type = "technical" if any(
        k in headline.lower() for k in ["cto","engineer","developer","ml","ai","data","research"]
    ) else "business"

    summary = (headline + (f" · {location}" if location else "")).strip() or "Experienced operator/founder."
    contacts = [linkedin] if linkedin else []
    sources  = [linkedin] if linkedin else []
    justification = f"Signals from position: {headline}" if headline else "Matches based on profile keywords."

    return {
        "name": name,
        "profile_type": profile_type,
        "summary": summary[:300],
        "contacts": contacts,
        "source_links": sources,
        "match_justification": justification,
    }