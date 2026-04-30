from __future__ import annotations

import csv
import html
import io
import json

from radar_marca.history import SnapshotDiff
from radar_marca.models import CandidateDomain, RiskChange


def to_json(results: list[CandidateDomain]) -> str:
    payload = [result.to_dict() for result in results]
    return json.dumps(payload, ensure_ascii=False, indent=2)


def to_text(results: list[CandidateDomain]) -> str:
    lines: list[str] = []
    for item in results:
        notes = ", ".join(item.notes) if item.notes else "-"
        sources = ", ".join(item.source_tags) if item.source_tags else "-"
        lines.append(
            f"- {item.domain} | similarity={item.similarity_score:.2f} | dns={item.dns_resolves} | http={item.http_reachable} | risk={item.risk_score} | sources={sources} | notes={notes}"
        )
    return "\n".join(lines)


def _markdown_findings(title: str, results: list[CandidateDomain], limit: int = 10) -> list[str]:
    lines = [title]
    if not results:
        lines.append("- Sin resultados")
        return lines
    for item in results[:limit]:
        notes = ", ".join(item.notes) if item.notes else "-"
        sources = ", ".join(item.source_tags) if item.source_tags else "-"
        title_hint = f", title: {item.title}" if item.title else ""
        lines.append(
            f"- **{item.domain}** — riesgo {item.risk_score}/100, similitud {item.similarity_score:.2f}, dns={item.dns_resolves}, http={item.http_reachable}, fuentes: {sources}, notas: {notes}{title_hint}"
        )
    return lines


def _markdown_risk_changes(title: str, changes: list[RiskChange], limit: int = 10) -> list[str]:
    lines = [title]
    if not changes:
        lines.append("- Ninguno")
        return lines
    for item in changes[:limit]:
        lines.append(f"- **{item.domain}** — {item.previous_risk} → {item.current_risk} ({item.delta:+d})")
    return lines


def to_markdown(
    brand: str,
    legitimate_domains: list[str],
    results: list[CandidateDomain],
    diff: SnapshotDiff | None = None,
) -> str:
    top_risky = [item for item in results if item.risk_score >= 50]
    lines = [
        f"# Informe RadarMarca: {brand}",
        "",
        "## Dominios legítimos",
    ]
    if legitimate_domains:
        lines.extend(f"- {domain}" for domain in legitimate_domains)
    else:
        lines.append("- No definidos")

    lines.extend(
        [
            "",
            "## Resumen",
            f"- Candidatos analizados: {len(results)}",
            f"- Riesgo alto (>=50): {len(top_risky)}",
            f"- Dominios con MX: {sum(1 for item in results if item.mx_records)}",
            f"- Dominios con título HTTP: {sum(1 for item in results if item.title)}",
        ]
    )

    if diff is not None:
        lines.extend(
            [
                f"- Nuevos desde snapshot anterior: {len(diff.new_domains)}",
                f"- Ya vistos: {len(diff.seen_domains)}",
                f"- Desaparecidos: {len(diff.removed_domains)}",
                f"- Riesgo al alza: {len(diff.rising_risk)}",
                f"- Riesgo a la baja: {len(diff.falling_risk)}",
            ]
        )

    lines.extend(["", *(_markdown_findings("## Hallazgos priorizados", results))])

    if diff is not None:
        lines.extend(["", *(_markdown_findings("## Nuevos hallazgos", diff.new_domains))])
        lines.extend(["", *(_markdown_findings("## Ya vistos (siguen presentes)", diff.seen_domains))])
        lines.extend(["", *(_markdown_risk_changes("## Riesgo al alza", diff.rising_risk))])
        lines.extend(["", *(_markdown_risk_changes("## Riesgo a la baja", diff.falling_risk))])
        lines.append("")
        lines.append("## Dominios desaparecidos")
        if diff.removed_domains:
            lines.extend(f"- {domain}" for domain in diff.removed_domains[:20])
        else:
            lines.append("- Ninguno")

    return "\n".join(lines)


def to_csv(results: list[CandidateDomain], diff: SnapshotDiff | None = None) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "domain",
        "similarity_score",
        "dns_resolves",
        "http_reachable",
        "risk_score",
        "notes",
        "status",
        "ns_records",
        "mx_records",
        "title",
        "fingerprint",
        "whois_summary",
        "source_tags",
    ])

    new_set = {item.domain for item in diff.new_domains} if diff else set()
    seen_set = {item.domain for item in diff.seen_domains} if diff else set()

    for item in results:
        if item.domain in new_set:
            status = "new"
        elif item.domain in seen_set:
            status = "seen"
        else:
            status = "current"
        writer.writerow(
            [
                item.domain,
                item.similarity_score,
                item.dns_resolves,
                item.http_reachable,
                item.risk_score,
                "|".join(item.notes),
                status,
                "|".join(item.ns_records),
                "|".join(item.mx_records),
                item.title or "",
                item.fingerprint or "",
                item.whois_summary or "",
                "|".join(item.source_tags),
            ]
        )
    return output.getvalue()


def _html_rows(results: list[CandidateDomain], label: str) -> str:
    rows = []
    for item in results[:15]:
        notes = html.escape(", ".join(item.notes) if item.notes else "-")
        title = html.escape(item.title or "-")
        sources = html.escape(", ".join(item.source_tags) if item.source_tags else "-")
        rows.append(
            "<tr>"
            f"<td>{html.escape(item.domain)}</td>"
            f"<td>{item.risk_score}</td>"
            f"<td>{item.similarity_score:.2f}</td>"
            f"<td>{'yes' if item.dns_resolves else 'no'}</td>"
            f"<td>{'yes' if item.http_reachable else 'no'}</td>"
            f"<td>{sources}</td>"
            f"<td>{title}</td>"
            f"<td>{notes}</td>"
            f"<td>{label}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _html_risk_changes(changes: list[RiskChange]) -> str:
    if not changes:
        return "<li>Ninguno</li>"
    return "".join(
        f"<li><strong>{html.escape(item.domain)}</strong>: {item.previous_risk} → {item.current_risk} ({item.delta:+d})</li>"
        for item in changes[:10]
    )


def to_html_dashboard(
    brand: str,
    legitimate_domains: list[str],
    results: list[CandidateDomain],
    diff: SnapshotDiff | None = None,
) -> str:
    top_risky = [item for item in results if item.risk_score >= 50]
    new_domains = diff.new_domains if diff else []
    seen_domains = diff.seen_domains if diff else results[:10]
    removed = diff.removed_domains if diff else []
    legit = "".join(f"<li>{html.escape(domain)}</li>" for domain in legitimate_domains) or "<li>No definidos</li>"

    return f"""<!doctype html>
<html lang=\"es\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>RadarMarca · {html.escape(brand)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #0b1020; color: #e5e7eb; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; }}
    .card {{ background: #121933; padding: 1rem; border-radius: 12px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ padding: 0.65rem; border-bottom: 1px solid #253056; text-align: left; font-size: 0.95rem; vertical-align: top; }}
    th {{ color: #93c5fd; }}
    h1, h2 {{ margin-top: 1.5rem; }}
    ul {{ padding-left: 1.2rem; }}
    a {{ color: #93c5fd; }}
  </style>
</head>
<body>
  <h1>RadarMarca · {html.escape(brand)}</h1>
  <div class=\"grid\">
    <div class=\"card\"><strong>{len(results)}</strong><br>Candidatos analizados</div>
    <div class=\"card\"><strong>{len(top_risky)}</strong><br>Riesgo alto</div>
    <div class=\"card\"><strong>{len(new_domains)}</strong><br>Nuevos</div>
    <div class=\"card\"><strong>{len(seen_domains)}</strong><br>Ya vistos</div>
  </div>

  <h2>Dominios legítimos</h2>
  <ul>{legit}</ul>

  <h2>Hallazgos priorizados</h2>
  <table>
    <thead><tr><th>Dominio</th><th>Riesgo</th><th>Similitud</th><th>DNS</th><th>HTTP</th><th>Fuentes</th><th>Título</th><th>Notas</th><th>Estado</th></tr></thead>
    <tbody>
      {_html_rows(new_domains, 'new')}
      {_html_rows(seen_domains, 'seen')}
      {_html_rows([item for item in results if item not in new_domains and item not in seen_domains], 'current')}
    </tbody>
  </table>

  <h2>Riesgo al alza</h2>
  <ul>{_html_risk_changes(diff.rising_risk if diff else [])}</ul>

  <h2>Riesgo a la baja</h2>
  <ul>{_html_risk_changes(diff.falling_risk if diff else [])}</ul>

  <h2>Desaparecidos</h2>
  <ul>{''.join(f'<li>{html.escape(domain)}</li>' for domain in removed[:20]) or '<li>Ninguno</li>'}</ul>
</body>
</html>
"""
