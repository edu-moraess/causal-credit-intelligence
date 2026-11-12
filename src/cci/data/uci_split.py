"""Deterministic, stratified index splitting for the UCI PD benchmark.

This is a predictive benchmark split only. The source's temporal cutoff is
insufficiently documented, so this module does not claim temporal validation.
No preprocessing, feature fitting, or model training is performed here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import load_uci_benchmark_contract


DEFAULT_SPLIT_CONFIG = Path("configs/splits/uci_credit_default_pd_v1.json")


def load_uci_split_config(
    root: str | Path | None = None,
    config_path: str | Path = DEFAULT_SPLIT_CONFIG,
) -> dict[str, Any]:
    """Load and validate the versioned UCI predictive split configuration."""
    project = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[3]
    path = (project / config_path).resolve()
    if not path.is_relative_to(project):
        raise DataContractError("Split config path must remain inside the project root.")
    if not path.is_file():
        raise FileNotFoundError(f"UCI split config not found: {path}")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataContractError(f"Unable to read UCI split config: {exc}") from exc

    if config.get("split_config_id") != "uci_credit_default_pd_v1":
        raise DataContractError("Unexpected UCI split config identifier.")
    ratios = config.get("ratios", {})
    names = ("train", "validation", "test")
    if set(ratios) != set(names):
        raise DataContractError("Split ratios must define train, validation, and test.")
    values = [float(ratios[name]) for name in names]
    if any(value <= 0.0 or value >= 1.0 for value in values):
        raise DataContractError("Every split ratio must be between 0 and 1.")
    if not np.isclose(sum(values), 1.0, atol=1e-12):
        raise DataContractError("Split ratios must sum to 1.")
    if not isinstance(config.get("random_seed"), int):
        raise DataContractError("random_seed must be an integer.")
    if config.get("strategy") != "stratified_random_by_target":
        raise DataContractError("Unsupported UCI split strategy.")
    return config


def _allocate_counts(size: int, ratios: list[float]) -> list[int]:
    raw = [size * ratio for ratio in ratios]
    counts = [int(value) for value in raw]
    remainder = size - sum(counts)
    # Stable tie-breaking follows train, validation, test order.
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i] - counts[i]), i))
    for index in order[:remainder]:
        counts[index] += 1
    if any(count == 0 for count in counts):
        raise DataContractError(
            "Each target class must contribute at least one row to every split.",
            context={"class_size": size, "allocated_counts": counts},
        )
    return counts


def create_uci_benchmark_splits(
    frame: Any,
    root: str | Path | None = None,
    contract: dict[str, Any] | None = None,
    split_config: dict[str, Any] | None = None,
) -> dict[str, np.ndarray]:
    """Return deterministic, disjoint positional indices for train/val/test.

    The function does not mutate the frame or fit any transformation. Indices
    are sorted within each split to preserve source row order when selecting.
    """
    if contract is None:
        contract = load_uci_benchmark_contract(root)
    if split_config is None:
        split_config = load_uci_split_config(root)

    target = contract["task"]["target"]
    allowed = set(contract["task"]["allowed_target_values"])
    if target not in frame.columns:
        raise DataContractError(f"Target column {target!r} is missing.")
    if frame[target].isna().any():
        raise DataContractError("Target contains missing values.")
    observed = set(frame[target].unique().tolist())
    if observed != allowed:
        raise DataContractError(
            "Target values do not match the configured binary classes.",
            context={"expected": sorted(allowed), "actual": sorted(observed)},
        )

    names = ("train", "validation", "test")
    ratios = [float(split_config["ratios"][name]) for name in names]
    rng = np.random.default_rng(split_config["random_seed"])
    buckets: dict[str, list[np.ndarray]] = {name: [] for name in names}

    target_values = frame[target].to_numpy()
    for class_value in sorted(allowed):
        class_indices = np.flatnonzero(target_values == class_value)
        shuffled = rng.permutation(class_indices)
        counts = _allocate_counts(len(shuffled), ratios)
        boundaries = np.cumsum([0] + counts)
        for split_index, name in enumerate(names):
            buckets[name].append(shuffled[boundaries[split_index]:boundaries[split_index + 1]])

    result = {
        name: np.sort(np.concatenate(parts)).astype(np.int64, copy=False)
        for name, parts in buckets.items()
    }

    all_indices = np.concatenate([result[name] for name in names])
    expected_indices = np.arange(len(frame), dtype=np.int64)
    if len(all_indices) != len(frame) or not np.array_equal(np.sort(all_indices), expected_indices):
        raise DataContractError("Split indices are not a complete, disjoint partition.")

    return result


def build_uci_split_manifest(
    frame: Any,
    splits: dict[str, np.ndarray],
    root: str | Path | None = None,
    contract: dict[str, Any] | None = None,
    split_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a compact audit manifest; does not persist files or train models."""
    if contract is None:
        contract = load_uci_benchmark_contract(root)
    if split_config is None:
        split_config = load_uci_split_config(root)
    target = contract["task"]["target"]
    manifest: dict[str, Any] = {
        "split_config_id": split_config["split_config_id"],
        "strategy": split_config["strategy"],
        "random_seed": split_config["random_seed"],
        "temporal_validation_claimed": False,
        "temporal_limitation": split_config["temporal_limitation"],
        "training_performed": False,
        "feature_transformations_fitted": False,
        "splits": {},
    }
    for name in ("train", "validation", "test"):
        indices = splits[name]
        counts = frame.iloc[indices][target].value_counts().to_dict()
        manifest["splits"][name] = {
            "rows": int(len(indices)),
            "target_counts": {str(key): int(value) for key, value in counts.items()},
        }
    return manifest
