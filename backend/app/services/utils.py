from typing import Dict, Any, List, Tuple

def candidate_key(p: Dict[str, Any]) -> Tuple[str, str]:
    """
    Unique-ish key for dedupe. Prefer LinkedIn publicIdentifier,
    else (name, position) as a fallback.
    """
    public_id = (p.get("publicIdentifier") or "").strip().lower()
    if public_id:
        return ("id", public_id)
    name = (p.get("name") or "").strip().lower()
    position = (p.get("position") or "").strip().lower()
    return (name, position)

def dedupe(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for p in raw:
        k = candidate_key(p)
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
    return out
