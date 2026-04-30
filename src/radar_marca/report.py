from __future__ import annotations

import json

from radar_marca.models import CandidateDomain


def to_json(results: list[CandidateDomain]) -> str:
    payload = [result.to_dict() for result in results]
    return json.dumps(payload, ensure_ascii=False, indent=2)


def to_text(results: list[CandidateDomain]) -> str:
    lines: list[str] = []
    for item in results:
        notes = ", ".join(item.notes) if item.notes else "-"
        lines.append(
            f"- {item.domain} | similarity={item.similarity_score:.2f} | dns={item.dns_resolves} | http={item.http_reachable} | risk={item.risk_score} | notes={notes}"
        )
    return "\n".join(lines)


def to_markdown(brand: str, legitimate_domains: list[str], results: list[CandidateDomain]) -> str:
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
            "",
            "## Hallazgos priorizados",
        ]
    )

    if not results:
        lines.append("- Sin resultados")
        return "\n".join(lines)

    for item in results[:10]:
        notes = ", ".join(item.notes) if item.notes else "-"
        lines.append(
            f"- **{item.domain}** — riesgo {item.risk_score}/100, similitud {item.similarity_score:.2f}, dns={item.dns_resolves}, http={item.http_reachable}, notas: {notes}"
        )

    return "\n".join(lines)
