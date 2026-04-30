from __future__ import annotations

import json
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from html import unescape

import dns.resolver


def fetch_crtsh_domains(brand: str, limit: int = 50) -> list[str]:
    query = urllib.parse.quote(f"%{brand}%")
    url = f"https://crt.sh/?q={query}&output=json"
    request = urllib.request.Request(url, headers={"User-Agent": "RadarMarca/0.4"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8", "ignore"))
    except Exception:
        return []

    domains: list[str] = []
    seen = set()
    for item in payload:
        for raw in str(item.get("name_value", "")).splitlines():
            domain = raw.strip().lower().lstrip("*.")
            if not domain or domain in seen:
                continue
            seen.add(domain)
            domains.append(domain)
            if len(domains) >= limit:
                return domains
    return domains


def dns_record_summary(domain: str) -> tuple[list[str], list[str]]:
    ns_records: list[str] = []
    mx_records: list[str] = []
    resolver = dns.resolver.Resolver(configure=True)
    resolver.lifetime = 3
    resolver.timeout = 3
    try:
        ns_records = sorted(str(r).rstrip(".") for r in resolver.resolve(domain, "NS"))
    except Exception:
        pass
    try:
        mx_records = sorted(str(r.exchange).rstrip(".") for r in resolver.resolve(domain, "MX"))
    except Exception:
        pass
    return ns_records, mx_records


def http_metadata(domain: str) -> tuple[str | None, str | None]:
    for scheme in ("https://", "http://"):
        request = urllib.request.Request(
            f"{scheme}{domain}",
            headers={"User-Agent": "RadarMarca/0.4"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                server = response.headers.get("server")
                body = response.read(8192).decode("utf-8", "ignore")
                title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
                title = unescape(title_match.group(1).strip()) if title_match else None
                fingerprint = server or response.headers.get("x-powered-by")
                return title, fingerprint
        except Exception:
            continue
    return None, None


def whois_summary(domain: str) -> str | None:
    whois_bin = shutil.which("whois")
    if not whois_bin:
        return None
    try:
        output = subprocess.check_output([whois_bin, domain], stderr=subprocess.DEVNULL, timeout=8, text=True)
    except Exception:
        return None

    interesting = []
    for line in output.splitlines():
        low = line.lower()
        if low.startswith(("registrar:", "creation date:", "registry expiry date:", "name server:")):
            interesting.append(line.strip())
        if len(interesting) >= 4:
            break
    return " | ".join(interesting) if interesting else None
