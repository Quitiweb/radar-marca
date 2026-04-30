import json

from radar_marca.models import BrandProfile, CandidateDomain
from radar_marca.storage import (
    brand_config_path,
    brand_storage_dir,
    list_brand_profiles,
    list_snapshots_for_brand,
    load_brand_profile,
    load_brand_profiles,
    load_snapshot,
    save_brand_dashboard,
    save_brand_profile,
    save_brand_report,
    save_snapshot,
)


def test_load_brand_profiles(tmp_path):
    source = tmp_path / "brands.json"
    source.write_text(
        json.dumps(
            [
                {
                    "client": "demo",
                    "brand": "Acme",
                    "legitimate_domains": ["acme.com"],
                    "whitelist": ["acme.es"],
                }
            ]
        ),
        encoding="utf-8",
    )

    profiles = load_brand_profiles(source)
    assert profiles == [BrandProfile(client="demo", brand="Acme", legitimate_domains=["acme.com"], whitelist=["acme.es"])]


def test_save_snapshot_and_report(tmp_path):
    results = [CandidateDomain(domain="aacme.com", similarity_score=0.88, risk_score=68, notes=["high_similarity"])]
    base_dir = brand_storage_dir("demo", "Acme", base_dir=tmp_path)
    snapshot = save_snapshot("Acme", results, base_dir=base_dir)
    report = save_brand_report("Acme", "# informe", base_dir=base_dir)
    dashboard = save_brand_dashboard("Acme", "<html></html>", base_dir=base_dir)

    assert snapshot.exists()
    assert report.exists()
    assert dashboard.exists()
    assert "results" in snapshot.read_text(encoding="utf-8")

    snapshots = list_snapshots_for_brand("Acme", base_dir=base_dir)
    assert snapshots == [snapshot]
    loaded = load_snapshot(snapshot)
    assert loaded["results"][0].domain == "aacme.com"


def test_save_and_load_brand_profile(tmp_path):
    profile = BrandProfile(client="agency", brand="Acme", legitimate_domains=["acme.com"], whitelist=["acme.es"])
    path = save_brand_profile(profile, base_dir=tmp_path)
    assert path == brand_config_path("agency", "Acme", base_dir=tmp_path)
    loaded = load_brand_profile(path)
    assert loaded == profile
    assert list_brand_profiles(tmp_path) == [path]
