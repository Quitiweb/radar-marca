from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class CandidateDomain:
    domain: str
    similarity_score: float
    dns_resolves: bool = False
    http_reachable: bool = False
    risk_score: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class BrandProfile:
    brand: str
    legitimate_domains: list[str] = field(default_factory=list)
    whitelist: list[str] = field(default_factory=list)
