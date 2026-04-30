from __future__ import annotations

from radar_marca.domain_generator import generate_candidate_domains
from radar_marca.models import BrandProfile, CandidateDomain
from radar_marca.resolvers import dns_resolves, http_reachable
from radar_marca.scorer import risk_score, similarity_score
from radar_marca.sources import dns_record_summary, fetch_crtsh_domains, http_metadata, whois_summary


def scan_brand(profile: BrandProfile, limit: int = 25, skip_http: bool = False) -> list[CandidateDomain]:
    primary_domain = profile.legitimate_domains[0] if profile.legitimate_domains else None
    generated = generate_candidate_domains(
        brand=profile.brand,
        legitimate_domain=primary_domain,
        limit=limit,
    )
    ct_candidates = fetch_crtsh_domains(profile.brand, limit=limit) if profile.watch_ct_logs else []

    candidates: list[tuple[str, list[str]]] = []
    seen_domains = set()
    for domain in generated:
        if domain not in seen_domains:
            candidates.append((domain, ["generated"]))
            seen_domains.add(domain)
    for domain in ct_candidates:
        if domain not in seen_domains:
            candidates.append((domain, ["crtsh"]))
            seen_domains.add(domain)
        else:
            for idx, (existing, tags) in enumerate(candidates):
                if existing == domain and "crtsh" not in tags:
                    candidates[idx] = (existing, [*tags, "crtsh"])
                    break

    whitelist = {domain.lower() for domain in profile.whitelist}
    whitelist.update(domain.lower() for domain in profile.legitimate_domains)

    results: list[CandidateDomain] = []
    for candidate, source_tags in candidates[: max(limit, len(candidates))]:
        sim = similarity_score(profile.brand, candidate)
        dns_ok = dns_resolves(candidate)
        http_ok = False if skip_http else http_reachable(candidate)
        risk, notes = risk_score(profile.brand, candidate, dns_ok, http_ok)
        ns_records, mx_records = dns_record_summary(candidate) if dns_ok else ([], [])
        title, fingerprint = (None, None) if skip_http else http_metadata(candidate)
        whois_text = whois_summary(candidate)

        if "crtsh" in source_tags:
            risk = min(100, risk + 10)
            notes.append("seen_in_ct_logs")
        if mx_records:
            risk = min(100, risk + 5)
            notes.append("mx_present")
        if title and profile.brand.lower() in title.lower():
            risk = min(100, risk + 10)
            notes.append("brand_in_title")
        if fingerprint:
            notes.append("fingerprint_present")
        if whois_text:
            notes.append("whois_available")

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
                ns_records=ns_records,
                mx_records=mx_records,
                title=title,
                fingerprint=fingerprint,
                whois_summary=whois_text,
                source_tags=source_tags,
            )
        )

    results.sort(key=lambda item: item.risk_score, reverse=True)
    return results[:limit]
