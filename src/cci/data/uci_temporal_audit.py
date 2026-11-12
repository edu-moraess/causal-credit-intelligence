"""Read-only temporal availability and leakage audit for the UCI PD benchmark.

The audit maps source-documented calendar periods but does not infer an
operational prediction cutoff, within-month data availability, or absence of
leakage. It never fits, transforms, or mutates the input frame.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import load_uci_benchmark_contract


DEFAULT_TEMPORAL_CONFIG = Path(
    "configs/audits/uci_credit_default_temporal_availability_v1.json"
)


def _project_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parents[3]


def load_uci_temporal_config(
    root: str | Path | None = None,
    config_path: str | Path = DEFAULT_TEMPORAL_CONFIG,
) -> dict[str, Any]:
    """Load the versioned source-temporal map from inside the project root."""
    project = _project_root(root)
    path = (project / config_path).resolve()
    if not path.is_relative_to(project):
        raise DataContractError("Temporal config path must remain inside the project root.")
    if not path.is_file():
        raise FileNotFoundError(f"UCI temporal config not found: {path}")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataContractError(f"Unable to read UCI temporal config: {exc}") from exc

    if config.get("audit_config_id") != "uci_credit_default_temporal_availability_v1":
        raise DataContractError("Unexpected UCI temporal config identifier.")
    if not isinstance(config.get("feature_temporal_metadata"), dict):
        raise DataContractError("Temporal config must define feature_temporal_metadata.")
    return config


def audit_uci_temporal_availability(
    frame: Any,
    root: str | Path | None = None,
    contract: dict[str, Any] | None = None,
    temporal_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit documented feature periods and unresolved operational availability.

    This is a documentation/contract audit, not a row-level timestamp audit:
    the UCI frame contains no per-record observation or feature-release times.
    """
    if contract is None:
        contract = load_uci_benchmark_contract(root)
    if temporal_config is None:
        temporal_config = load_uci_temporal_config(root)

    expected_columns = contract["data_expectations"]["column_names"]
    if list(frame.columns) != expected_columns:
        raise DataContractError(
            "Frame columns or order do not match the UCI benchmark contract."
        )

    task = contract["task"]
    target = task["target"]
    features = list(task["features"])
    if target not in frame.columns or frame[target].isna().any():
        raise DataContractError("Target is missing or contains null values.")
    observed_target = set(frame[target].unique().tolist())
    allowed_target = set(task["allowed_target_values"])
    if observed_target != allowed_target:
        raise DataContractError(
            "Target values do not match the UCI benchmark contract.",
            context={"expected": sorted(allowed_target), "actual": sorted(observed_target)},
        )

    metadata = temporal_config["feature_temporal_metadata"]
    if set(metadata) != set(features):
        raise DataContractError(
            "Temporal metadata must cover every contract feature exactly once.",
            context={
                "missing": sorted(set(features) - set(metadata)),
                "unexpected": sorted(set(metadata) - set(features)),
            },
        )

    field_audit: dict[str, Any] = {}
    monthly_fields: dict[str, list[str]] = {}
    for feature in features:
        item = metadata[feature]
        temporal_class = item.get("temporal_classification")
        if temporal_class not in {
            "monthly_observation_without_release_timestamp",
            "point_in_time_value_without_as_of_date",
            "static_attribute_without_reference_date",
        }:
            raise DataContractError(
                f"Unsupported temporal classification for feature {feature!r}."
            )

        reference_month = item.get("reference_month")
        if temporal_class == "monthly_observation_without_release_timestamp":
            if not isinstance(reference_month, str) or not re.fullmatch(
                r"\d{4}-(0[1-9]|1[0-2])", reference_month
            ):
                raise DataContractError(
                    f"Monthly feature {feature!r} requires a YYYY-MM reference_month."
                )
            monthly_fields.setdefault(reference_month, []).append(feature)
            availability_reason = (
                "The source documents the calendar month, but not the exact "
                "measurement, statement-close, publication, or availability timestamp."
            )
            period_status = "calendar_month_documented"
        else:
            if reference_month is not None:
                raise DataContractError(
                    f"Non-monthly feature {feature!r} must not declare reference_month."
                )
            if temporal_class == "point_in_time_value_without_as_of_date":
                availability_reason = (
                    "The source describes a point-in-time credit amount but does not "
                    "provide its as-of date or a history of changes."
                )
            else:
                availability_reason = (
                    "The source provides a demographic attribute without a "
                    "measurement/reference date or update history."
                )
            period_status = "reference_date_not_documented"

        field_audit[feature] = {
            "temporal_classification": temporal_class,
            "reference_month": reference_month,
            "reference_period_status": period_status,
            "availability_at_operational_cutoff": "unresolved",
            "availability_reason": availability_reason,
            "potential_leakage_status": "not_determined",
        }

    target_metadata = temporal_config["target_temporal_metadata"]
    if target_metadata.get("target_column") != target:
        raise DataContractError("Temporal target metadata does not match the contract target.")
    if target_metadata.get("calendar_window") is not None:
        raise DataContractError(
            "The current UCI source audit must not assert an undocumented target calendar window."
        )

    documented_months = sorted(monthly_fields)
    return {
        "audit_id": "uci_pd_temporal_availability_v1",
        "rows": int(len(frame)),
        "feature_count": len(features),
        "identifier_excluded": contract["identifier"]["column"] not in features,
        "target_excluded_from_features": target not in features,
        "source_temporal_scope": {
            "documented_predictor_period_start": temporal_config[
                "source_temporal_scope"
            ]["predictor_period_start"],
            "documented_predictor_period_end": temporal_config[
                "source_temporal_scope"
            ]["predictor_period_end"],
            "latest_documented_predictor_month": documented_months[-1]
            if documented_months
            else None,
            "exact_operational_observation_cutoff": None,
            "cutoff_status": "not_documented",
        },
        "monthly_feature_groups": {
            month: sorted(columns) for month, columns in sorted(monthly_fields.items())
        },
        "target_temporal_assessment": {
            "target_column": target,
            "horizon_description": target_metadata["horizon_description"],
            "calendar_window": None,
            "calendar_window_status": "not_documented",
            "event_timestamp_available": False,
        },
        "field_audit": field_audit,
        "availability_summary": {
            "certified_available_at_operational_cutoff": 0,
            "unresolved": len(features),
            "all_features_certified_available": False,
        },
        "leakage_assessment": {
            "status": "not_determined",
            "reason": (
                "The dataset does not provide a precise operational cutoff or "
                "within-month feature availability timestamps. No claim of "
                "absence or presence of leakage can be made from this audit."
            ),
            "temporal_validation_supported": False,
        },
        "training_authorized": False,
        "preprocessing_fitted": False,
        "frame_modified": False,
        "causal_effect_estimation_supported": False,
        "production_use_authorized": False,
    }
