from radar_marca.scorer import risk_score, similarity_score


def test_similarity_score_high_for_close_match():
    assert similarity_score("acme", "acm3.com") > 0.70


def test_risk_score_adds_notes_for_active_suspicious_domain():
    score, notes = risk_score("acme", "secureacme-login.com", dns_resolves=True, http_reachable=True)
    assert score > 50
    assert "active_dns" in notes
    assert any(note.startswith("keyword:") for note in notes)
