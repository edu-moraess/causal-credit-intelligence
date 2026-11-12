from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import load_uci_benchmark_contract
from cci.data.uci_split import (
    build_uci_split_manifest,
    create_uci_benchmark_splits,
    load_uci_split_config,
)


ROOT = Path(__file__).resolve().parents[2]


def _fixture():
    contract = load_uci_benchmark_contract(ROOT)
    config = load_uci_split_config(ROOT)
    target = contract["task"]["target"]
    frame = pd.DataFrame({
        target: [0] * 77 + [1] * 23,
        "ID": np.arange(100, 200),
    })
    return frame, contract, config


def test_split_config_is_versioned_and_non_temporal():
    config = load_uci_split_config(ROOT)
    assert config["split_config_id"] == "uci_credit_default_pd_v1"
    assert config["strategy"] == "stratified_random_by_target"
    assert config["temporal_validation_claimed"] is False
    assert sum(config["ratios"].values()) == pytest.approx(1.0)


def test_split_is_deterministic_complete_disjoint_and_stratified():
    frame, contract, config = _fixture()
    first = create_uci_benchmark_splits(frame, ROOT, contract, config)
    second = create_uci_benchmark_splits(frame, ROOT, contract, config)

    for name in ("train", "validation", "test"):
        np.testing.assert_array_equal(first[name], second[name])
    joined = np.concatenate(list(first.values()))
    assert len(joined) == len(frame)
    assert len(np.unique(joined)) == len(frame)
    np.testing.assert_array_equal(np.sort(joined), np.arange(len(frame)))

    target = contract["task"]["target"]
    for name, indices in first.items():
        rate = frame.iloc[indices][target].mean()
        assert abs(rate - frame[target].mean()) < 0.06


def test_split_does_not_mutate_source_frame():
    frame, contract, config = _fixture()
    before = frame.copy(deep=True)
    create_uci_benchmark_splits(frame, ROOT, contract, config)
    pd.testing.assert_frame_equal(frame, before)


def test_split_rejects_missing_or_unexpected_target_values():
    frame, contract, config = _fixture()
    target = contract["task"]["target"]
    frame.loc[0, target] = np.nan
    with pytest.raises(DataContractError):
        create_uci_benchmark_splits(frame, ROOT, contract, config)

    frame.loc[0, target] = 2
    with pytest.raises(DataContractError):
        create_uci_benchmark_splits(frame, ROOT, contract, config)


def test_split_config_path_cannot_escape_project_root(tmp_path):
    with pytest.raises(DataContractError):
        load_uci_split_config(tmp_path, "../../outside.json")


def test_manifest_records_scope_and_no_training():
    frame, contract, config = _fixture()
    splits = create_uci_benchmark_splits(frame, ROOT, contract, config)
    manifest = build_uci_split_manifest(frame, splits, ROOT, contract, config)
    assert manifest["temporal_validation_claimed"] is False
    assert manifest["training_performed"] is False
    assert manifest["feature_transformations_fitted"] is False
    assert sum(item["rows"] for item in manifest["splits"].values()) == len(frame)
