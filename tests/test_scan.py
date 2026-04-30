from radar_marca.models import BrandProfile
from radar_marca.scan import scan_brand


def test_scan_brand_whitelists_legitimate_domains(monkeypatch):
    monkeypatch.setattr("radar_marca.scan.dns_resolves", lambda domain: True)
    monkeypatch.setattr("radar_marca.scan.http_reachable", lambda domain: True)
    monkeypatch.setattr("radar_marca.scan.dns_record_summary", lambda domain: (["ns1.example.com"], ["mx.example.com"]))
    monkeypatch.setattr("radar_marca.scan.http_metadata", lambda domain: ("Acme Login", "nginx"))
    monkeypatch.setattr("radar_marca.scan.whois_summary", lambda domain: "Registrar: Example")
    monkeypatch.setattr("radar_marca.scan.fetch_crtsh_domains", lambda brand, limit: ["secureacme-login.com"])
    monkeypatch.setattr(
        "radar_marca.scan.generate_candidate_domains",
        lambda brand, legitimate_domain, limit: ["acme.es", "secureacme-login.com"],
    )

    profile = BrandProfile(
        brand="Acme",
        legitimate_domains=["acme.com"],
        whitelist=["acme.es"],
    )
    results = scan_brand(profile, limit=5, skip_http=False)

    assert results[0].domain == "secureacme-login.com"
    assert results[0].risk_score > 0
    assert "crtsh" in results[0].source_tags
    whitelisted = next(item for item in results if item.domain == "acme.es")
    assert whitelisted.risk_score == 0
    assert whitelisted.notes == ["whitelisted"]
