import json

from radar_marca.models import BrandProfile, CandidateDomain
from radar_marca.storage import load_brand_profiles, save_brand_report, save_snapshot


def test_load_brand_profiles(tmp_path):
    source = tmp_path / "brands.json"
    source.write_text(
        json.dumps(
            [
                {
                    "brand": "Acme",
                    "legitimate_domains": ["acme.com"],
                    "whitelist": ["acme.es"],
                }
            ]
        ),
        encoding="utf-8",
    )

    profiles = load_brand_profiles(source)
    assert profiles == [BrandProfile(brand="Acme", legitimate_domains=["acme.com"], whitelist=["acme.es"])]


def test_save_snapshot_and_report(tmp_path):
    results = [CandidateDomain(domain="aacme.com", similarity_score=0.88, risk_score=68, notes=["high_similarity"])]
    snapshot = save_snapshot("Acme", results, base_dir=tmp_path)
    report = save_brand_report("Acme", "# informe", base_dir=tmp_path)

    assert snapshot.exists()
    assert report.exists()
    assert "results" in snapshot.read_text(encoding="utf-8")
