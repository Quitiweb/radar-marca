from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from radar_marca.models import BrandProfile, CandidateDomain


DEFAULT_DATA_DIR = Path("data")


def ensure_data_dir(base_dir: str | Path = DEFAULT_DATA_DIR) -> Path:
    path = Path(base_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_brand_profiles(path: str | Path) -> list[BrandProfile]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    profiles: list[BrandProfile] = []
    for item in payload:
        profiles.append(
            BrandProfile(
                brand=item["brand"],
                legitimate_domains=item.get("legitimate_domains", []),
                whitelist=item.get("whitelist", []),
            )
        )
    return profiles


def snapshot_filename(brand: str) -> str:
    safe_brand = "".join(ch.lower() if ch.isalnum() else "-" for ch in brand).strip("-")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{safe_brand}-{timestamp}.json"


def save_snapshot(brand: str, results: list[CandidateDomain], base_dir: str | Path = DEFAULT_DATA_DIR) -> Path:
    target_dir = ensure_data_dir(base_dir) / "snapshots"
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / snapshot_filename(brand)
    payload = {
        "brand": brand,
        "generated_at": datetime.now(UTC).isoformat(),
        "results": [result.to_dict() for result in results],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def save_brand_report(brand: str, content: str, base_dir: str | Path = DEFAULT_DATA_DIR) -> Path:
    target_dir = ensure_data_dir(base_dir) / "reports"
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_brand = "".join(ch.lower() if ch.isalnum() else "-" for ch in brand).strip("-")
    path = target_dir / f"{safe_brand}-latest.md"
    path.write_text(content, encoding="utf-8")
    return path
