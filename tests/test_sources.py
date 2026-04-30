from radar_marca.sources import fetch_crtsh_domains


def test_fetch_crtsh_domains_handles_failures(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("boom")))
    assert fetch_crtsh_domains("Acme") == []
