"""Diagnostics result contract; no diagnostics are fabricated."""
from dataclasses import dataclass, field


@dataclass
class DiagnosticsReport:
    status: str = "not_run"
    checks: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
