"""Read-only feature-readiness and descriptive fairness audit for UCI PD data.

This module profiles raw columns and group-level outcome rates. It does not
choose a model feature set, encode categories, infer undocumented semantics,
or compute formal fairness metrics.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import load_uci_benchmark_contract


def audit_uci_feature_readiness(
    frame: Any,
    root: str | Path | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a JSON-serializable profile without mutating or fitting on frame."""
    if contract is None:
        contract = load_uci_benchmark_contract(root)

    task = contract["task"]
    target = task["target"]
    identifier = contract["identifier"]["column"]
    features = list(task["features"])
    expected = contract["data_expectations"]["column_names"]
    fairness_fields = contract["governance"]["attributes_requiring_fairness_review"]

    missing = [column for column in expected if column not in frame.columns]
    unexpected = [column for column in frame.columns if column not in expected]
    if missing or unexpected:
        raise DataContractError(
            "Frame columns do not match the UCI benchmark contract.",
            context={"missing": missing, "unexpected": unexpected},
        )
    if target not in frame.columns or identifier not in frame.columns:
        raise DataContractError("Identifier or target column is missing.")
    if frame[target].isna().any():
        raise DataContractError("Target contains missing values.")

    # These are descriptive engineering groups, not final modeling decisions.
    nominal = ["SEX", "EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
    numeric = [
        "LIMIT_BAL", "AGE",
        "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
        "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
    ]
    if set(nominal + numeric) != set(features) or len(nominal + numeric) != len(features):
        raise DataContractError("Feature audit groups do not partition the contract feature list.")

    columns: dict[str, Any] = {}
    for column in nominal:
        series = frame[column]
        counts = series.value_counts(dropna=False).sort_index()
        columns[column] = {
            "proposed_role": "discrete_nominal_code",
            "observed_value_counts": {str(key): int(value) for key, value in counts.items()},
            "semantic_relabeling_performed": False,
            "ordinal_distance_assumed": False,
        }
    for column in numeric:
        series = pd.to_numeric(frame[column], errors="coerce")
        if series.isna().any():
            raise DataContractError(
                f"Numeric feature {column!r} contains missing or non-numeric values."
            )
        quantiles = series.quantile([0.01, 0.25, 0.50, 0.75, 0.99])
        columns[column] = {
            "proposed_role": "continuous_numeric",
            "min": float(series.min()),
            "p01": float(quantiles.loc[0.01]),
            "p25": float(quantiles.loc[0.25]),
            "median": float(quantiles.loc[0.50]),
            "p75": float(quantiles.loc[0.75]),
            "p99": float(quantiles.loc[0.99]),
            "max": float(series.max()),
            "negative_value_count": int((series < 0).sum()),
        }

    group_audit: dict[str, Any] = {}
    for column in fairness_fields:
        if column not in frame.columns:
            raise DataContractError(f"Fairness-review attribute {column!r} is missing.")
        grouped = frame.groupby(column, dropna=False)[target].agg(["count", "mean"])
        group_audit[column] = {
            "status": "descriptive_only_not_a_fairness_assessment",
            "groups": {
                str(key): {
                    "rows": int(row["count"]),
                    "positive_outcome_rate": float(row["mean"]),
                }
                for key, row in grouped.iterrows()
            },
        }

    target_counts = frame[target].value_counts().sort_index()
    return {
        "audit_id": "uci_pd_feature_readiness_v1",
        "rows": int(len(frame)),
        "feature_count": len(features),
        "identifier_excluded": identifier not in features,
        "target_excluded_from_features": target not in features,
        "target_counts": {str(key): int(value) for key, value in target_counts.items()},
        "target_positive_rate": float(frame[target].mean()),
        "feature_groups": {
            "nominal_discrete": nominal,
            "continuous_numeric": numeric,
            "fairness_review": list(fairness_fields),
        },
        "columns": columns,
        "descriptive_group_outcomes": group_audit,
        "feature_availability": {
            "status": "unresolved",
            "reason": contract["temporal_scope"]["restriction"],
            "deployment_readiness": False,
        },
        "semantic_relabeling_performed": False,
        "transformations_fitted": False,
        "training_performed": False,
        "formal_fairness_metrics_computed": False,
        "causal_effect_estimation_supported": False,
    }
