from __future__ import annotations

import argparse

from radar_marca.history import compare_snapshot_files, latest_snapshot_diff
from radar_marca.models import BrandProfile
from radar_marca.report import to_csv, to_html_dashboard, to_json, to_markdown, to_text
from radar_marca.scan import scan_brand
from radar_marca.storage import (
    brand_storage_dir,
    latest_snapshot_for_brand,
    list_brand_profiles,
    load_brand_profile,
    load_brand_profiles,
    save_brand_csv,
    save_brand_dashboard,
    save_brand_profile,
    save_brand_report,
    save_snapshot,
)
from radar_marca.webapp import run_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="radar-marca")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_brand = subparsers.add_parser("init-brand", help="Create a stable brand config")
    init_brand.add_argument("--brand", required=True)
    init_brand.add_argument("--client", default="default")
    init_brand.add_argument("--domain", action="append", default=[])
    init_brand.add_argument("--whitelist", action="append", default=[])
    init_brand.add_argument("--disable-ct", action="store_true")

    scan = subparsers.add_parser("scan", help="Scan candidate domains for a brand")
    scan.add_argument("--brand", required=True)
    scan.add_argument("--client", default="default")
    scan.add_argument("--domain", action="append", default=[])
    scan.add_argument("--whitelist", action="append", default=[])
    scan.add_argument("--limit", type=int, default=25)
    scan.add_argument("--json", action="store_true")
    scan.add_argument("--skip-http", action="store_true")
    scan.add_argument("--save-snapshot", action="store_true")
    scan.add_argument("--save-report", action="store_true")
    scan.add_argument("--save-csv", action="store_true")
    scan.add_argument("--save-html", action="store_true")
    scan.add_argument("--use-config", action="store_true", help="Load stable config for this client/brand if it exists")

    scan_file = subparsers.add_parser("scan-file", help="Scan brands from a JSON file")
    scan_file.add_argument("--input", required=True)
    scan_file.add_argument("--limit", type=int, default=25)
    scan_file.add_argument("--skip-http", action="store_true")
    scan_file.add_argument("--save-snapshot", action="store_true")
    scan_file.add_argument("--save-report", action="store_true")
    scan_file.add_argument("--save-csv", action="store_true")
    scan_file.add_argument("--save-html", action="store_true")

    diff = subparsers.add_parser("diff", help="Compare two snapshots or the latest two snapshots for a brand")
    diff.add_argument("--brand")
    diff.add_argument("--client", default="default")
    diff.add_argument("--previous")
    diff.add_argument("--current")

    serve = subparsers.add_parser("serve", help="Run local web viewer")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=5000)

    list_profiles_cmd = subparsers.add_parser("list-brands", help="List saved brand configs")
    return parser


def _profile_base_dir(profile: BrandProfile):
    return brand_storage_dir(profile.client, profile.brand)


def _emit_artifacts(profile: BrandProfile, results, diff, save_snapshot_flag, save_report_flag, save_csv_flag, save_html_flag) -> None:
    base_dir = _profile_base_dir(profile)
    if save_snapshot_flag:
        previous_snapshot = latest_snapshot_for_brand(profile.brand, base_dir=base_dir)
        snapshot_path = save_snapshot(profile.brand, results, base_dir=base_dir)
        print(f"\nSnapshot guardado en: {snapshot_path}")
        if previous_snapshot is not None:
            diff = compare_snapshot_files(previous_snapshot, snapshot_path)

    if save_report_flag:
        report_content = to_markdown(profile.brand, profile.legitimate_domains, results, diff=diff)
        report_path = save_brand_report(profile.brand, report_content, base_dir=base_dir)
        print(f"Informe guardado en: {report_path}")
    if save_csv_flag:
        csv_content = to_csv(results, diff=diff)
        csv_path = save_brand_csv(profile.brand, csv_content, base_dir=base_dir)
        print(f"CSV guardado en: {csv_path}")
    if save_html_flag:
        html_content = to_html_dashboard(profile.brand, profile.legitimate_domains, results, diff=diff)
        html_path = save_brand_dashboard(profile.brand, html_content, base_dir=base_dir)
        print(f"Dashboard HTML guardado en: {html_path}")


def _emit_results(profile: BrandProfile, results, output_json: bool, save_snapshot_flag: bool, save_report_flag: bool, save_csv_flag: bool, save_html_flag: bool) -> None:
    diff = latest_snapshot_diff(profile.brand, base_dir=_profile_base_dir(profile))
    print(to_json(results) if output_json else to_text(results))
    _emit_artifacts(profile, results, diff, save_snapshot_flag, save_report_flag, save_csv_flag, save_html_flag)


def _load_stable_profile_or_inline(brand: str, client: str, domains: list[str], whitelist: list[str], use_config: bool) -> BrandProfile:
    profile_path = None
    if use_config:
        for path in list_brand_profiles():
            loaded = load_brand_profile(path)
            if loaded.brand == brand and loaded.client == client:
                profile_path = path
                break
    if profile_path:
        return load_brand_profile(profile_path)
    return BrandProfile(brand=brand, client=client, legitimate_domains=domains, whitelist=whitelist)


def run_init_brand(brand: str, client: str, domains: list[str], whitelist: list[str], disable_ct: bool) -> int:
    profile = BrandProfile(
        brand=brand,
        client=client,
        legitimate_domains=domains,
        whitelist=whitelist,
        watch_ct_logs=not disable_ct,
    )
    path = save_brand_profile(profile)
    print(f"Config guardada en: {path}")
    return 0


def run_scan(brand: str, client: str, domains: list[str], whitelist: list[str], limit: int, output_json: bool, skip_http: bool, save_snapshot_flag: bool, save_report_flag: bool, save_csv_flag: bool, save_html_flag: bool, use_config: bool) -> int:
    profile = _load_stable_profile_or_inline(brand, client, domains, whitelist, use_config=use_config)
    results = scan_brand(profile=profile, limit=limit, skip_http=skip_http)
    _emit_results(profile, results, output_json, save_snapshot_flag, save_report_flag, save_csv_flag, save_html_flag)
    return 0


def run_scan_file(input_path: str, limit: int, skip_http: bool, save_snapshot_flag: bool, save_report_flag: bool, save_csv_flag: bool, save_html_flag: bool) -> int:
    profiles = load_brand_profiles(input_path)
    for idx, profile in enumerate(profiles):
        results = scan_brand(profile=profile, limit=limit, skip_http=skip_http)
        if idx:
            print("\n" + "=" * 60)
        print(f"# {profile.client}/{profile.brand}")
        _emit_results(profile, results, output_json=False, save_snapshot_flag=save_snapshot_flag, save_report_flag=save_report_flag, save_csv_flag=save_csv_flag, save_html_flag=save_html_flag)
    return 0


def run_diff(brand: str | None, client: str, previous: str | None, current: str | None) -> int:
    if previous and current:
        diff = compare_snapshot_files(previous, current)
    elif brand:
        base_dir = brand_storage_dir(client, brand)
        diff = latest_snapshot_diff(brand, base_dir=base_dir)
        if diff is None:
            raise SystemExit(f"No hay suficientes snapshots para {client}/{brand}")
    else:
        raise SystemExit("Debes indicar --brand o bien --previous y --current")

    print(f"Nuevos: {len(diff.new_domains)}")
    print(f"Ya vistos: {len(diff.seen_domains)}")
    print(f"Desaparecidos: {len(diff.removed_domains)}")
    print(f"Riesgo al alza: {len(diff.rising_risk)}")
    print(f"Riesgo a la baja: {len(diff.falling_risk)}")
    if diff.new_domains:
        print("\nTop nuevos:")
        print(to_text(diff.new_domains[:10]))
    return 0


def run_list_brands() -> int:
    for path in list_brand_profiles():
        profile = load_brand_profile(path)
        print(f"- {profile.client}/{profile.brand} -> {path}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-brand":
        return run_init_brand(args.brand, args.client, args.domain, args.whitelist, args.disable_ct)
    if args.command == "scan":
        return run_scan(args.brand, args.client, args.domain, args.whitelist, args.limit, args.json, args.skip_http, args.save_snapshot, args.save_report, args.save_csv, args.save_html, args.use_config)
    if args.command == "scan-file":
        return run_scan_file(args.input, args.limit, args.skip_http, args.save_snapshot, args.save_report, args.save_csv, args.save_html)
    if args.command == "diff":
        return run_diff(args.brand, args.client, args.previous, args.current)
    if args.command == "serve":
        run_server(host=args.host, port=args.port)
        return 0
    if args.command == "list-brands":
        return run_list_brands()

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
