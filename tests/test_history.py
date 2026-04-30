from pathlib import Path

from radar_marca.history import compare_result_sets, compare_snapshot_files
from radar_marca.models import CandidateDomain


def test_compare_result_sets_detects_new_seen_removed_and_risk_changes():
    previous = [
        CandidateDomain(domain="old.com", similarity_score=0.7, risk_score=40),
        CandidateDomain(domain="same.com", similarity_score=0.8, risk_score=50),
        CandidateDomain(domain="drop.com", similarity_score=0.8, risk_score=70),
    ]
    current = [
        CandidateDomain(domain="same.com", similarity_score=0.8, risk_score=65),
        CandidateDomain(domain="new.com", similarity_score=0.9, risk_score=80),
        CandidateDomain(domain="drop.com", similarity_score=0.8, risk_score=60),
    ]

    diff = compare_result_sets(previous, current)
    assert [item.domain for item in diff.new_domains] == ["new.com"]
    assert [item.domain for item in diff.seen_domains] == ["same.com", "drop.com"]
    assert diff.removed_domains == ["old.com"]
    assert diff.rising_risk[0].domain == "same.com"
    assert diff.falling_risk[0].domain == "drop.com"


def test_compare_snapshot_files(tmp_path: Path):
    previous = tmp_path / "acme-1.json"
    current = tmp_path / "acme-2.json"
    previous.write_text('{"brand": "Acme", "results": [{"domain": "old.com", "similarity_score": 0.7, "dns_resolves": false, "http_reachable": false, "risk_score": 40, "notes": [], "ns_records": [], "mx_records": [], "title": null, "fingerprint": null, "whois_summary": null, "source_tags": []}]}', encoding="utf-8")
    current.write_text('{"brand": "Acme", "results": [{"domain": "new.com", "similarity_score": 0.9, "dns_resolves": true, "http_reachable": false, "risk_score": 80, "notes": ["high_similarity"], "ns_records": [], "mx_records": [], "title": null, "fingerprint": null, "whois_summary": null, "source_tags": ["generated"]}]}', encoding="utf-8")

    diff = compare_snapshot_files(previous, current)
    assert diff.previous_path == previous
    assert diff.current_path == current
    assert [item.domain for item in diff.new_domains] == ["new.com"]
