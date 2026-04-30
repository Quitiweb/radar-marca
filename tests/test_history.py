from pathlib import Path

from radar_marca.history import compare_result_sets, compare_snapshot_files
from radar_marca.models import CandidateDomain


def test_compare_result_sets_detects_new_seen_and_removed():
    previous = [
        CandidateDomain(domain="old.com", similarity_score=0.7, risk_score=40),
        CandidateDomain(domain="same.com", similarity_score=0.8, risk_score=50),
    ]
    current = [
        CandidateDomain(domain="same.com", similarity_score=0.8, risk_score=55),
        CandidateDomain(domain="new.com", similarity_score=0.9, risk_score=80),
    ]

    diff = compare_result_sets(previous, current)
    assert [item.domain for item in diff.new_domains] == ["new.com"]
    assert [item.domain for item in diff.seen_domains] == ["same.com"]
    assert diff.removed_domains == ["old.com"]


def test_compare_snapshot_files(tmp_path: Path):
    previous = tmp_path / "acme-1.json"
    current = tmp_path / "acme-2.json"
    previous.write_text('{"brand": "Acme", "results": [{"domain": "old.com", "similarity_score": 0.7, "dns_resolves": false, "http_reachable": false, "risk_score": 40, "notes": []}]}', encoding="utf-8")
    current.write_text('{"brand": "Acme", "results": [{"domain": "new.com", "similarity_score": 0.9, "dns_resolves": true, "http_reachable": false, "risk_score": 80, "notes": ["high_similarity"]}]}', encoding="utf-8")

    diff = compare_snapshot_files(previous, current)
    assert diff.previous_path == previous
    assert diff.current_path == current
    assert [item.domain for item in diff.new_domains] == ["new.com"]
