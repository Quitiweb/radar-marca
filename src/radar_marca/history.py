from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from radar_marca.models import CandidateDomain, RiskChange
from radar_marca.storage import load_snapshot, list_snapshots_for_brand


@dataclass(slots=True)
class SnapshotDiff:
    previous_path: Path | None
    current_path: Path | None
    new_domains: list[CandidateDomain]
    seen_domains: list[CandidateDomain]
    removed_domains: list[str]
    rising_risk: list[RiskChange] = field(default_factory=list)
    falling_risk: list[RiskChange] = field(default_factory=list)
    unchanged_risk: list[RiskChange] = field(default_factory=list)


def compare_result_sets(previous: list[CandidateDomain], current: list[CandidateDomain]) -> SnapshotDiff:
    previous_map = {item.domain: item for item in previous}
    current_map = {item.domain: item for item in current}

    new_domains = [item for domain, item in current_map.items() if domain not in previous_map]
    seen_domains = [item for domain, item in current_map.items() if domain in previous_map]
    removed_domains = sorted(domain for domain in previous_map if domain not in current_map)

    rising_risk: list[RiskChange] = []
    falling_risk: list[RiskChange] = []
    unchanged_risk: list[RiskChange] = []
    for domain, current_item in current_map.items():
        previous_item = previous_map.get(domain)
        if not previous_item:
            continue
        delta = current_item.risk_score - previous_item.risk_score
        change = RiskChange(domain=domain, previous_risk=previous_item.risk_score, current_risk=current_item.risk_score, delta=delta)
        if delta > 0:
            rising_risk.append(change)
        elif delta < 0:
            falling_risk.append(change)
        else:
            unchanged_risk.append(change)

    new_domains.sort(key=lambda item: item.risk_score, reverse=True)
    seen_domains.sort(key=lambda item: item.risk_score, reverse=True)
    rising_risk.sort(key=lambda item: item.delta, reverse=True)
    falling_risk.sort(key=lambda item: item.delta)

    return SnapshotDiff(
        previous_path=None,
        current_path=None,
        new_domains=new_domains,
        seen_domains=seen_domains,
        removed_domains=removed_domains,
        rising_risk=rising_risk,
        falling_risk=falling_risk,
        unchanged_risk=unchanged_risk,
    )


def compare_snapshot_files(previous_path: Path, current_path: Path) -> SnapshotDiff:
    previous_payload = load_snapshot(previous_path)
    current_payload = load_snapshot(current_path)
    diff = compare_result_sets(previous_payload["results"], current_payload["results"])
    diff.previous_path = previous_path
    diff.current_path = current_path
    return diff


def latest_snapshot_diff(brand: str, base_dir: str | Path = "data") -> SnapshotDiff | None:
    snapshots = list_snapshots_for_brand(brand, base_dir=base_dir)
    if len(snapshots) < 2:
        return None
    return compare_snapshot_files(snapshots[-2], snapshots[-1])
