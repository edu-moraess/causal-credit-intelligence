"""Deterministic structural checks. No causal estimates are computed here."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cci.core.exceptions import DataContractError, DataLeakageError


@dataclass
class ValidationReport:
    checks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors

    def add(self, name: str, passed: bool, detail: str = "", severity: str = "error") -> None:
        self.checks.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed and detail:
            (self.errors if severity == "error" else self.warnings).append(detail)

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "checks": self.checks,
                "errors": self.errors, "warnings": self.warnings}


def validate_schema(frame: Any, required_columns: tuple[str, ...] | list[str]) -> ValidationReport:
    report = ValidationReport()
    missing = sorted(set(required_columns) - set(getattr(frame, "columns", [])))
    report.add("required_columns", not missing, f"Missing columns: {missing}" if missing else "All required columns present")
    return report


def validate_types(frame: Any, date_columns: tuple[str, ...] = ("observation_date",)) -> ValidationReport:
    report = ValidationReport()
    for col in date_columns:
        if col in frame.columns:
            try:
                import pandas as pd
                parsed = pd.to_datetime(frame[col], errors="coerce")
                invalid = int(parsed.isna().sum())
            except Exception as exc:
                report.add(f"datetime:{col}", False, f"Could not validate {col}: {exc}")
                continue
            report.add(f"datetime:{col}", invalid == 0, f"{invalid} invalid/missing date values" if invalid else "Valid datetime values")
    return report


def check_missingness(frame: Any, threshold: float = 0.30) -> ValidationReport:
    report = ValidationReport()
    if len(frame) == 0:
        report.add("non_empty", False, "Dataset is empty")
        return report
    rates = frame.isna().mean()
    for col, rate in rates.items():
        report.add(f"missingness:{col}", float(rate) <= threshold,
                   f"{col}: missingness {float(rate):.3f} exceeds {threshold:.3f}" if float(rate) > threshold else "")
    return report


def check_duplicates(frame: Any, subset: tuple[str, ...] | list[str] = ("customer_id", "observation_date")) -> ValidationReport:
    report = ValidationReport()
    available = [c for c in subset if c in frame.columns]
    if not available:
        report.add("duplicates", True, "No configured duplicate key columns found", severity="warning")
        return report
    count = int(frame.duplicated(subset=available, keep=False).sum())
    report.add("duplicates", count == 0, f"{count} rows belong to duplicate keys {available}" if count else "No duplicate keys")
    return report


def check_temporal_consistency(frame: Any, observation_date: str = "observation_date") -> ValidationReport:
    report = ValidationReport()
    if observation_date not in frame.columns:
        report.add("temporal_consistency", False, f"Missing temporal column: {observation_date}")
        return report
    import pandas as pd
    dates = pd.to_datetime(frame[observation_date], errors="coerce")
    valid = dates.notna().all()
    report.add("temporal_consistency", bool(valid), "Invalid observation dates found" if not valid else "Observation dates parse successfully")
    return report


def check_leakage(covariates: list[str] | tuple[str, ...], forbidden: list[str] | tuple[str, ...]) -> ValidationReport:
    overlap = sorted(set(covariates) & set(forbidden))
    report = ValidationReport()
    report.add("post_treatment_leakage", not overlap,
               f"Forbidden post-treatment fields in covariates: {overlap}" if overlap else "No configured post-treatment fields in covariates")
    return report


def run_structural_validation(frame: Any, contract: Any = None) -> ValidationReport:
    required = contract.required_columns() if contract else ("customer_id", "observation_date")
    reports = [validate_schema(frame, required), validate_types(frame),
               check_missingness(frame), check_duplicates(frame), check_temporal_consistency(frame)]
    merged = ValidationReport()
    for item in reports:
        merged.checks.extend(item.checks)
        merged.errors.extend(item.errors)
        merged.warnings.extend(item.warnings)
    return merged


def assert_no_leakage(covariates: list[str], forbidden: list[str]) -> None:
    report = check_leakage(covariates, forbidden)
    if not report.passed:
        raise DataLeakageError("; ".join(report.errors))
