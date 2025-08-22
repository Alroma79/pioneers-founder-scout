from typing import Dict, Any

def score_candidate(person: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
    text = (person.get("summary") or "") + " " + (person.get("match_justification") or "")
    tl = text.lower()
    score = 0

    if any(k in tl for k in ["founder","co-founder","exit"]): score += 25
    if any(k in tl for k in ["cto","engineer","developer","ml","ai","data","research"]):
        score += 25 if criteria.get("technical_signal", True) else 10
    if any(k in tl for k in ["phd","msc","master"]): score += 10
    sector = (criteria.get("sector") or "").lower()
    if sector and sector in tl: score += 15
    if any(k in tl for k in ["head of","director","vp","c-level","chief","lead"]): score += 15

    score = max(0, min(100, score))
    person["score"] = score
    # Adjusted thresholds: A=80+, B=60+, C=<60 for more meaningful tiers
    person["tier"] = "A" if score >= 80 else "B" if score >= 60 else "C"
    return person
