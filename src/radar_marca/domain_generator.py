from __future__ import annotations

import itertools
import re

COMMON_SUFFIXES = [
    "app",
    "digital",
    "group",
    "global",
    "login",
    "online",
    "secure",
    "support",
    "verify",
    "vip",
    "shop",
    "pay",
]

COMMON_TLDS = [".com", ".net", ".org", ".io", ".co", ".es"]


def normalize_brand(brand: str) -> str:
    normalized = re.sub(r"[^a-z0-9]", "", brand.lower())
    if not normalized:
        raise ValueError("brand must contain at least one alphanumeric character")
    return normalized


def _single_char_deletions(value: str) -> set[str]:
    return {value[:i] + value[i + 1 :] for i in range(len(value)) if len(value) > 3}


def _adjacent_swaps(value: str) -> set[str]:
    out = set()
    for i in range(len(value) - 1):
        chars = list(value)
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
        out.add("".join(chars))
    return out


def _repeated_char_variants(value: str) -> set[str]:
    out = set()
    for i, ch in enumerate(value):
        out.add(value[:i] + ch + value[i:])
    return out


def generate_candidate_domains(brand: str, legitimate_domain: str | None = None, limit: int = 50) -> list[str]:
    base = normalize_brand(brand)
    stem = legitimate_domain.split(".")[0].lower() if legitimate_domain else base

    variants = {base, stem}
    variants |= _single_char_deletions(base)
    variants |= _adjacent_swaps(base)
    variants |= _repeated_char_variants(base)
    variants |= {f"{base}{suffix}" for suffix in COMMON_SUFFIXES}
    variants |= {f"{suffix}{base}" for suffix in ["my", "get", "go", "try", "the"]}
    variants |= {"".join(p) for p in itertools.product([base, stem], repeat=1)}

    candidates = []
    seen = set()
    for variant in sorted(variants):
        for tld in COMMON_TLDS:
            domain = f"{variant}{tld}"
            if legitimate_domain and domain == legitimate_domain.lower():
                continue
            if domain not in seen:
                seen.add(domain)
                candidates.append(domain)
            if len(candidates) >= limit:
                return candidates
    return candidates
