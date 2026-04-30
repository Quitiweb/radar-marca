from __future__ import annotations

from difflib import SequenceMatcher


RISK_KEYWORDS = {
    "login": 20,
    "secure": 20,
    "verify": 20,
    "support": 10,
    "pay": 10,
    "shop": 5,
}


def similarity_score(brand: str, domain: str) -> float:
    hostname = domain.split(".")[0].lower()
    score = SequenceMatcher(None, brand.lower(), hostname).ratio()
    return round(score, 4)


def risk_score(brand: str, domain: str, dns_resolves: bool, http_reachable: bool) -> tuple[int, list[str]]:
    notes: list[str] = []
    score = 0

    similarity = similarity_score(brand, domain)
    score += int(similarity * 60)
    if similarity >= 0.85:
        notes.append("high_similarity")
    elif similarity >= 0.70:
        notes.append("moderate_similarity")

    if dns_resolves:
        score += 15
        notes.append("active_dns")

    if http_reachable:
        score += 15
        notes.append("http_reachable")

    hostname = domain.split(".")[0].lower()
    for keyword, weight in RISK_KEYWORDS.items():
        if keyword in hostname:
            score += weight
            notes.append(f"keyword:{keyword}")

    return min(score, 100), notes
