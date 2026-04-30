from radar_marca.models import BrandProfile
from radar_marca.storage import brand_storage_dir, save_brand_dashboard, save_brand_profile
from radar_marca.webapp import create_app


def test_webapp_serves_index_and_brand_report(tmp_path):
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    save_brand_profile(BrandProfile(client="demo", brand="Acme", legitimate_domains=["acme.com"]), base_dir=config_dir)
    base_dir = brand_storage_dir("demo", "Acme", base_dir=data_dir)
    save_brand_dashboard("Acme", "<html><body>ok</body></html>", base_dir=base_dir)

    app = create_app(data_dir=data_dir, config_dir=config_dir)
    client = app.test_client()

    index = client.get("/")
    assert index.status_code == 200
    assert b"Acme" in index.data

    report = client.get("/brand/demo/acme")
    assert report.status_code == 200
    assert b"ok" in report.data
