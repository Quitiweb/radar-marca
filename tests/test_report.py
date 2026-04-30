from radar_marca.history import SnapshotDiff
from radar_marca.models import CandidateDomain, RiskChange
from radar_marca.report import to_csv, to_html_dashboard, to_markdown


def _sample_results():
    return [
        CandidateDomain(domain="new.com", similarity_score=0.91, dns_resolves=True, http_reachable=True, risk_score=82, notes=["high_similarity"], source_tags=["generated"]),
        CandidateDomain(domain="seen.com", similarity_score=0.75, dns_resolves=True, http_reachable=False, risk_score=55, notes=["active_dns"], source_tags=["crtsh"], title="Seen"),
    ]


def test_to_csv_marks_statuses():
    results = _sample_results()
    diff = SnapshotDiff(previous_path=None, current_path=None, new_domains=[results[0]], seen_domains=[results[1]], removed_domains=[])
    csv_text = to_csv(results, diff=diff)
    assert "new.com" in csv_text
    assert ",new" in csv_text
    assert ",seen" in csv_text
    assert "source_tags" in csv_text


def test_to_markdown_and_html_include_history_sections():
    results = _sample_results()
    diff = SnapshotDiff(
        previous_path=None,
        current_path=None,
        new_domains=[results[0]],
        seen_domains=[results[1]],
        removed_domains=["gone.com"],
        rising_risk=[RiskChange(domain="seen.com", previous_risk=40, current_risk=55, delta=15)],
        falling_risk=[],
        unchanged_risk=[],
    )
    markdown = to_markdown("Acme", ["acme.com"], results, diff=diff)
    html = to_html_dashboard("Acme", ["acme.com"], results, diff=diff)
    assert "Nuevos hallazgos" in markdown
    assert "Riesgo al alza" in markdown
    assert "gone.com" in markdown
    assert "<html" in html.lower()
    assert "new.com" in html
