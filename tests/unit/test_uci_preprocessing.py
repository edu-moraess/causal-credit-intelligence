from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import load_uci_benchmark_contract
from cci.data.uci_preprocessing import (
    build_uci_preprocessor,
    load_uci_preprocessing_config,
    prepare_uci_pd_partitions,
)


ROOT = Path(__file__).resolve().parents[2]
pytest.importorskip("sklearn")


def _fixture():
    contract = load_uci_benchmark_contract(ROOT)
    config = load_uci_preprocessing_config(ROOT)
    rng = np.random.default_rng(17)
    rows = 40
    frame = pd.DataFrame({
        "ID": np.arange(1000, 1000 + rows),
        "LIMIT_BAL": rng.normal(150000, 30000, rows),
        "SEX": rng.choice([1, 2], rows),
        "EDUCATION": rng.choice([0, 1, 2, 3, 4, 5, 6], rows),
        "MARRIAGE": rng.choice([0, 1, 2, 3], rows),
        "AGE": rng.integers(21, 70, rows),
        **{f"PAY_{name}": rng.choice([-2, -1, 0, 1, 2, 3], rows)
           for name in ("0", "2", "3", "4", "5", "6")},
        **{f"BILL_AMT{i}": rng.normal(0, 50000, rows) for i in range(1, 7)},
        **{f"PAY_AMT{i}": rng.normal(0, 15000, rows) for i in range(1, 7)},
        "default payment next month": np.array([0, 1] * 20),
    })
    splits = {
        "train": np.arange(0, 24, dtype=np.int64),
        "validation": np.arange(24, 32, dtype=np.int64),
        "test": np.arange(32, 40, dtype=np.int64),
    }
    return frame, splits, contract, config


def test_preprocessing_groups_partition_features_and_exclude_id_target():
    frame, _, contract, config = _fixture()
    transformer = build_uci_preprocessor(ROOT, contract, config)
    assert set(config["feature_groups"]["nominal_discrete"] + config["feature_groups"]["continuous_numeric"]) == set(contract["task"]["features"])
    assert "ID" not in contract["task"]["features"]
    assert contract["task"]["target"] not in contract["task"]["features"]
    assert transformer is not None


def test_fit_occurs_on_train_only_and_other_partitions_are_transform_only():
    frame, splits, contract, config = _fixture()
    before = frame.copy(deep=True)
    result = prepare_uci_pd_partitions(frame, splits, ROOT, contract, config)
    assert result["preprocessing_fit_partition"] == "train"
    assert result["validation_used_for_fitting"] is False
    assert result["test_used_for_fitting"] is False
    assert result["training_performed"] is False
    assert result["identifier_in_features"] is False
    assert result["target_in_features"] is False
    assert result["X"]["train"].shape[0] == 24
    assert result["X"]["validation"].shape[0] == 8
    assert result["X"]["test"].shape[0] == 8
    pd.testing.assert_frame_equal(frame, before)


def test_split_overlap_or_missing_rows_is_rejected():
    frame, splits, contract, config = _fixture()
    splits["validation"] = np.arange(20, 28, dtype=np.int64)
    with pytest.raises(DataContractError):
        prepare_uci_pd_partitions(frame, splits, ROOT, contract, config)


def test_missing_values_fail_fast_without_implicit_imputation():
    frame, splits, contract, config = _fixture()
    frame.loc[0, "AGE"] = np.nan
    with pytest.raises(DataContractError):
        prepare_uci_pd_partitions(frame, splits, ROOT, contract, config)


def test_preprocessor_is_unfitted_when_built():
    frame, _, contract, config = _fixture()
    transformer = build_uci_preprocessor(ROOT, contract, config)
    with pytest.raises(Exception):
        transformer.transform(frame[contract["task"]["features"]].iloc[:2])
