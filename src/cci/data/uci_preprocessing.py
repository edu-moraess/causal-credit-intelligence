"""Train-only preprocessing for the retrospective UCI PD benchmark.

The helper fits transformations exclusively on the training partition.
It never mutates the source frame, includes the identifier/target as features,
or performs model training.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import load_uci_benchmark_contract


DEFAULT_PREPROCESSING_CONFIG = Path(
    "configs/preprocessing/uci_credit_default_pd_preprocessing_v1.json"
)
SPLIT_NAMES = ("train", "validation", "test")


def load_uci_preprocessing_config(
    root: str | Path | None = None,
    config_path: str | Path = DEFAULT_PREPROCESSING_CONFIG,
) -> dict[str, Any]:
    project = (
        Path(root).resolve()
        if root is not None
        else Path(__file__).resolve().parents[3]
    )
    path = (project / config_path).resolve()
    if not path.is_relative_to(project):
        raise DataContractError("Preprocessing config must remain inside project root.")
    if not path.is_file():
        raise FileNotFoundError(f"Preprocessing config not found: {path}")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataContractError(f"Unable to read preprocessing config: {exc}") from exc
    if config.get("preprocessing_config_id") != "uci_credit_default_pd_preprocessing_v1":
        raise DataContractError("Unexpected UCI preprocessing config identifier.")
    return config


def build_uci_preprocessor(
    root: str | Path | None = None,
    contract: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
):
    """Build an unfitted sklearn ColumnTransformer; requires the optional ml extra."""
    if contract is None:
        contract = load_uci_benchmark_contract(root)
    if config is None:
        config = load_uci_preprocessing_config(root)

    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    groups = config["feature_groups"]
    nominal = list(groups["nominal_discrete"])
    numeric = list(groups["continuous_numeric"])
    features = list(contract["task"]["features"])
    if len(nominal + numeric) != len(features) or set(nominal + numeric) != set(features):
        raise DataContractError("Preprocessing groups must partition the contract features.")
    if contract["identifier"]["column"] in nominal + numeric:
        raise DataContractError("Identifier cannot enter preprocessing.")
    if contract["task"]["target"] in nominal + numeric:
        raise DataContractError("Target cannot enter preprocessing.")

    nominal_cfg = config["nominal_transform"]
    numeric_cfg = config["numeric_transform"]
    if nominal_cfg["method"] != "one_hot_encoder" or nominal_cfg["handle_unknown"] != "ignore":
        raise DataContractError("Unsupported nominal encoding policy.")
    if numeric_cfg["method"] != "standard_scaler" or numeric_cfg["clipping"] or numeric_cfg["winsorization"]:
        raise DataContractError("Unsupported numeric transformation policy.")

    return ColumnTransformer(
        transformers=[
            ("nominal", OneHotEncoder(handle_unknown="ignore"), nominal),
            ("numeric", StandardScaler(), numeric),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


def prepare_uci_pd_partitions(
    frame: Any,
    splits: dict[str, np.ndarray],
    root: str | Path | None = None,
    contract: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fit preprocessing on train only and transform validation/test without fitting.

    Returns transformed feature matrices, copied target arrays, the fitted
    transformer, and feature names. This function does not fit a predictive
    estimator or inspect test performance.
    """
    import pandas as pd

    if contract is None:
        contract = load_uci_benchmark_contract(root)
    if config is None:
        config = load_uci_preprocessing_config(root)
    if not isinstance(frame, pd.DataFrame):
        raise DataContractError("UCI preprocessing expects a pandas DataFrame.")

    features = list(contract["task"]["features"])
    identifier = contract["identifier"]["column"]
    target = contract["task"]["target"]
    required = set(features + [identifier, target])
    if not required.issubset(frame.columns):
        raise DataContractError("Frame is missing required contract columns.")
    if frame[features + [target]].isna().to_numpy().any():
        raise DataContractError("Missing values found; imputation is not configured.")

    if set(splits) != set(SPLIT_NAMES):
        raise DataContractError("Splits must contain train, validation, and test.")
    indices: dict[str, np.ndarray] = {}
    for name in SPLIT_NAMES:
        values = np.asarray(splits[name])
        if values.ndim != 1 or not np.issubdtype(values.dtype, np.integer):
            raise DataContractError(f"{name} indices must be a one-dimensional integer array.")
        if len(values) == 0 or np.any(values < 0) or np.any(values >= len(frame)):
            raise DataContractError(f"{name} indices are empty or out of bounds.")
        indices[name] = values.astype(np.int64, copy=False)
    combined = np.concatenate([indices[name] for name in SPLIT_NAMES])
    if len(np.unique(combined)) != len(frame) or not np.array_equal(
        np.sort(combined), np.arange(len(frame), dtype=np.int64)
    ):
        raise DataContractError("Splits must form a complete, disjoint frame partition.")

    X = frame.loc[:, features]
    y = frame[target].to_numpy(copy=True)
    transformer = build_uci_preprocessor(root, contract, config)
    train_idx = indices["train"]
    X_train = transformer.fit_transform(X.iloc[train_idx])
    transformed = {
        "train": X_train,
        "validation": transformer.transform(X.iloc[indices["validation"]]),
        "test": transformer.transform(X.iloc[indices["test"]]),
    }
    return {
        "X": transformed,
        "y": {name: y[indices[name]].copy() for name in SPLIT_NAMES},
        "transformer": transformer,
        "feature_names": transformer.get_feature_names_out().tolist(),
        "feature_count": int(len(transformer.get_feature_names_out())),
        "training_performed": False,
        "preprocessing_fit_partition": "train",
        "validation_used_for_fitting": False,
        "test_used_for_fitting": False,
        "identifier_in_features": False,
        "target_in_features": False,
        "source_frame_modified": False,
    }
