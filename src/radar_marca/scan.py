from __future__ import annotations

from radar_marca.domain_generator import generate_candidate_domains
from radar_marca.models import BrandProfile, CandidateDomain
from radar_marca.resolvers import dns_resolves, http_reachable
from radar_marca.scorer import risk_score, similarity_score


def scan_brand(profile: BrandProfile, limit: int = 25, skip_http: bool = False) -> list[CandidateDomain]:
    primary_domain = profile.legitimate_domains[0] if profile.legitimate_domains else None
    candidates = generate_candidate_domains(
        brand=profile.brand,
        legitimate_domain=primary_domain,
        limit=limit,
    )

    whitelist = {domain.lower() for domain in profile.whitelist}
    whitelist.update(domain.lower() for domain in profile.legitimate_domains)

    results: list[CandidateDomain] = []
    for candidate in candidates:
        sim = similarity_score(profile.brand, candidate)
        dns_ok = dns_resolves(candidate)
        http_ok = False if skip_http else http_reachable(candidate)
        risk, notes = risk_score(profile.brand, candidate, dns_ok, http_ok)

        if candidate.lower() in whitelist:
            risk = 0
            notes = ["whitelisted"]

        results.append(
            CandidateDomain(
                domain=candidate,
                similarity_score=sim,
                dns_resolves=dns_ok,
                http_reachable=http_ok,
                risk_score=risk,
                notes=notes,
            )
        )

    results.sort(key=lambda item: item.risk_score, reverse=True)
    return results
