from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class CandidateDomain:
    domain: str
    similarity_score: float
    dns_resolves: bool = False
    http_reachable: bool = False
    risk_score: int = 0
    notes: list[str] = field(default_factory=list)
    ns_records: list[str] = field(default_factory=list)
    mx_records: list[str] = field(default_factory=list)
    title: str | None = None
    fingerprint: str | None = None
    whois_summary: str | None = None
    source_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class BrandProfile:
    brand: str
    legitimate_domains: list[str] = field(default_factory=list)
    whitelist: list[str] = field(default_factory=list)
    client: str = "default"
    watch_ct_logs: bool = True


@dataclass(slots=True)
class RiskChange:
    domain: str
    previous_risk: int
    current_risk: int
    delta: int
