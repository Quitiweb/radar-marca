from radar_marca.domain_generator import generate_candidate_domains, normalize_brand


def test_normalize_brand():
    assert normalize_brand("Radar Marca") == "radarmarca"


def test_generate_candidate_domains_excludes_legitimate_domain():
    candidates = generate_candidate_domains("Acme", legitimate_domain="acme.com", limit=20)
    assert "acme.com" not in candidates
    assert candidates
