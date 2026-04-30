from __future__ import annotations

import argparse

from radar_marca.history import compare_snapshot_files, latest_snapshot_diff
from radar_marca.models import BrandProfile
from radar_marca.report import to_csv, to_html_dashboard, to_json, to_markdown, to_text
from radar_marca.scan import scan_brand
from radar_marca.storage import (
    latest_snapshot_for_brand,
    load_brand_profiles,
    save_brand_csv,
    save_brand_dashboard,
    save_brand_report,
    save_snapshot,
)


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
    scan.add_argument("--save-csv", action="store_true", help="Save a CSV report under data/reports")
    scan.add_argument("--save-html", action="store_true", help="Save a HTML dashboard under data/reports")

    scan_file = subparsers.add_parser("scan-file", help="Scan brands from a JSON file")
    scan_file.add_argument("--input", required=True, help="Path to brands JSON file")
    scan_file.add_argument("--limit", type=int, default=25, help="Maximum generated candidates per brand")
    scan_file.add_argument("--skip-http", action="store_true", help="Skip HTTP reachability checks")
    scan_file.add_argument("--save-snapshot", action="store_true", help="Save a JSON snapshot per brand")
    scan_file.add_argument("--save-report", action="store_true", help="Save a markdown report per brand")
    scan_file.add_argument("--save-csv", action="store_true", help="Save a CSV report per brand")
    scan_file.add_argument("--save-html", action="store_true", help="Save a HTML dashboard per brand")

    diff = subparsers.add_parser("diff", help="Compare two snapshots or the latest two snapshots for a brand")
    diff.add_argument("--brand", help="Brand name to compare using latest snapshots")
    diff.add_argument("--previous", help="Path to previous snapshot JSON")
    diff.add_argument("--current", help="Path to current snapshot JSON")
    return parser


def _emit_artifacts(
    profile: BrandProfile,
    results,
    diff,
    save_snapshot_flag: bool,
    save_report_flag: bool,
    save_csv_flag: bool,
    save_html_flag: bool,
) -> None:
    if save_snapshot_flag:
        previous_snapshot = latest_snapshot_for_brand(profile.brand)
        snapshot_path = save_snapshot(profile.brand, results)
        print(f"\nSnapshot guardado en: {snapshot_path}")
        if previous_snapshot is not None:
            diff = compare_snapshot_files(previous_snapshot, snapshot_path)

    if save_report_flag:
        report_content = to_markdown(profile.brand, profile.legitimate_domains, results, diff=diff)
        report_path = save_brand_report(profile.brand, report_content)
        print(f"Informe guardado en: {report_path}")
    if save_csv_flag:
        csv_content = to_csv(results, diff=diff)
        csv_path = save_brand_csv(profile.brand, csv_content)
        print(f"CSV guardado en: {csv_path}")
    if save_html_flag:
        html_content = to_html_dashboard(profile.brand, profile.legitimate_domains, results, diff=diff)
        html_path = save_brand_dashboard(profile.brand, html_content)
        print(f"Dashboard HTML guardado en: {html_path}")


def _emit_results(
    profile: BrandProfile,
    results,
    output_json: bool,
    save_snapshot_flag: bool,
    save_report_flag: bool,
    save_csv_flag: bool,
    save_html_flag: bool,
) -> None:
    diff = latest_snapshot_diff(profile.brand)
    print(to_json(results) if output_json else to_text(results))
    _emit_artifacts(profile, results, diff, save_snapshot_flag, save_report_flag, save_csv_flag, save_html_flag)


def run_scan(
    brand: str,
    domains: list[str],
    whitelist: list[str],
    limit: int,
    output_json: bool,
    skip_http: bool,
    save_snapshot_flag: bool,
    save_report_flag: bool,
    save_csv_flag: bool,
    save_html_flag: bool,
) -> int:
    profile = BrandProfile(brand=brand, legitimate_domains=domains, whitelist=whitelist)
    results = scan_brand(profile=profile, limit=limit, skip_http=skip_http)
    _emit_results(profile, results, output_json, save_snapshot_flag, save_report_flag, save_csv_flag, save_html_flag)
    return 0


def run_scan_file(
    input_path: str,
    limit: int,
    skip_http: bool,
    save_snapshot_flag: bool,
    save_report_flag: bool,
    save_csv_flag: bool,
    save_html_flag: bool,
) -> int:
    profiles = load_brand_profiles(input_path)
    for idx, profile in enumerate(profiles):
        results = scan_brand(profile=profile, limit=limit, skip_http=skip_http)
        if idx:
            print("\n" + "=" * 60)
        print(f"# {profile.brand}")
        _emit_results(profile, results, output_json=False, save_snapshot_flag=save_snapshot_flag, save_report_flag=save_report_flag, save_csv_flag=save_csv_flag, save_html_flag=save_html_flag)
    return 0


def run_diff(brand: str | None, previous: str | None, current: str | None) -> int:
    if previous and current:
        diff = compare_snapshot_files(previous, current)
    elif brand:
        diff = latest_snapshot_diff(brand)
        if diff is None:
            raise SystemExit(f"No hay suficientes snapshots para {brand}")
    else:
        raise SystemExit("Debes indicar --brand o bien --previous y --current")

    print(f"Nuevos: {len(diff.new_domains)}")
    print(f"Ya vistos: {len(diff.seen_domains)}")
    print(f"Desaparecidos: {len(diff.removed_domains)}")
    if diff.new_domains:
        print("\nTop nuevos:")
        print(to_text(diff.new_domains[:10]))
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
            save_csv_flag=args.save_csv,
            save_html_flag=args.save_html,
        )
    if args.command == "scan-file":
        return run_scan_file(
            input_path=args.input,
            limit=args.limit,
            skip_http=args.skip_http,
            save_snapshot_flag=args.save_snapshot,
            save_report_flag=args.save_report,
            save_csv_flag=args.save_csv,
            save_html_flag=args.save_html,
        )
    if args.command == "diff":
        return run_diff(brand=args.brand, previous=args.previous, current=args.current)

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
