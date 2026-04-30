from __future__ import annotations

import argparse

from radar_marca.models import BrandProfile
from radar_marca.report import to_json, to_markdown, to_text
from radar_marca.scan import scan_brand
from radar_marca.storage import load_brand_profiles, save_brand_report, save_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="radar-marca")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan candidate domains for a brand")
    scan.add_argument("--brand", required=True, help="Brand name to analyze")
    scan.add_argument("--domain", action="append", default=[], help="Known legitimate domain, e.g. example.com")
    scan.add_argument("--whitelist", action="append", default=[], help="Domains to suppress in risk output")
    scan.add_argument("--limit", type=int, default=25, help="Maximum generated candidates")
    scan.add_argument("--json", action="store_true", help="Output JSON")
    scan.add_argument("--skip-http", action="store_true", help="Skip HTTP reachability checks")
    scan.add_argument("--save-snapshot", action="store_true", help="Save a JSON snapshot under data/snapshots")
    scan.add_argument("--save-report", action="store_true", help="Save a markdown report under data/reports")

    scan_file = subparsers.add_parser("scan-file", help="Scan brands from a JSON file")
    scan_file.add_argument("--input", required=True, help="Path to brands JSON file")
    scan_file.add_argument("--limit", type=int, default=25, help="Maximum generated candidates per brand")
    scan_file.add_argument("--skip-http", action="store_true", help="Skip HTTP reachability checks")
    scan_file.add_argument("--save-snapshot", action="store_true", help="Save a JSON snapshot per brand")
    scan_file.add_argument("--save-report", action="store_true", help="Save a markdown report per brand")
    return parser


def _emit_results(profile: BrandProfile, results, output_json: bool, save_snapshot_flag: bool, save_report_flag: bool) -> None:
    print(to_json(results) if output_json else to_text(results))
    if save_snapshot_flag:
        snapshot_path = save_snapshot(profile.brand, results)
        print(f"\nSnapshot guardado en: {snapshot_path}")
    if save_report_flag:
        report_content = to_markdown(profile.brand, profile.legitimate_domains, results)
        report_path = save_brand_report(profile.brand, report_content)
        print(f"Informe guardado en: {report_path}")


def run_scan(
    brand: str,
    domains: list[str],
    whitelist: list[str],
    limit: int,
    output_json: bool,
    skip_http: bool,
    save_snapshot_flag: bool,
    save_report_flag: bool,
) -> int:
    profile = BrandProfile(brand=brand, legitimate_domains=domains, whitelist=whitelist)
    results = scan_brand(profile=profile, limit=limit, skip_http=skip_http)
    _emit_results(profile, results, output_json, save_snapshot_flag, save_report_flag)
    return 0


def run_scan_file(input_path: str, limit: int, skip_http: bool, save_snapshot_flag: bool, save_report_flag: bool) -> int:
    profiles = load_brand_profiles(input_path)
    for idx, profile in enumerate(profiles):
        results = scan_brand(profile=profile, limit=limit, skip_http=skip_http)
        if idx:
            print("\n" + "=" * 60)
        print(f"# {profile.brand}")
        _emit_results(profile, results, output_json=False, save_snapshot_flag=save_snapshot_flag, save_report_flag=save_report_flag)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        return run_scan(
            brand=args.brand,
            domains=args.domain,
            whitelist=args.whitelist,
            limit=args.limit,
            output_json=args.json,
            skip_http=args.skip_http,
            save_snapshot_flag=args.save_snapshot,
            save_report_flag=args.save_report,
        )
    if args.command == "scan-file":
        return run_scan_file(
            input_path=args.input,
            limit=args.limit,
            skip_http=args.skip_http,
            save_snapshot_flag=args.save_snapshot,
            save_report_flag=args.save_report,
        )

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
