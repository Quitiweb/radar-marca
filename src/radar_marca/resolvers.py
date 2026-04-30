from __future__ import annotations

import socket
import urllib.error
import urllib.request


DEFAULT_TIMEOUT = 3


def dns_resolves(domain: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    previous = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        socket.gethostbyname(domain)
        return True
    except OSError:
        return False
    finally:
        socket.setdefaulttimeout(previous)


def http_reachable(domain: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    for scheme in ("https://", "http://"):
        request = urllib.request.Request(
            f"{scheme}{domain}",
            headers={"User-Agent": "RadarMarca/0.1"},
            method="HEAD",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return 200 <= getattr(response, "status", 0) < 500
        except (urllib.error.URLError, ValueError, TimeoutError):
            continue
    return False
