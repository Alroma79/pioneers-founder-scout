from typing import Dict, Any

def normalize_person(raw: Dict[str, Any]) -> Dict[str, Any]:
    # Map provider schema → our internal fields. Adjust keys to Harvest response.
    name = raw.get("name") or raw.get("full_name") or raw.get("title") or "Unknown"
    headline = raw.get("headline") or raw.get("bio") or ""
    linkedin = raw.get("linkedin_url") or raw.get("profile_url")

    profile_type = "technical" if any(k in (headline or "").lower()
                                      for k in ["cto","engineer","developer","ml","ai","data"]) else "business"

    summary = headline[:300] if headline else "Experienced operator/founder."
    contacts = [linkedin] if linkedin else []
    sources = [linkedin] if linkedin else []
    justification = f"Signals: {headline}" if headline else "Matches based on profile keywords."

    return {
        "name": name,
        "profile_type": profile_type,
        "summary": summary,
        "contacts": contacts,
        "source_links": sources,
        "match_justification": justification,
    }
