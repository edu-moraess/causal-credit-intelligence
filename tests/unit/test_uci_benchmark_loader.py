import json
from pathlib import Path

import pandas as pd
import pytest

from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import (
    load_uci_benchmark_contract,
    validate_uci_benchmark_frame,
)


ROOT = Path(__file__).resolve().parents[2]


def _contract():
    return load_uci_benchmark_contract(ROOT)


def _small_frame(contract):
    columns = contract["data_expectations"]["column_names"]
    frame = pd.DataFrame({column: [1, 2] for column in columns})
    frame["ID"] = [101, 102]
    frame["default payment next month"] = [0, 1]
    return frame


def test_loader_reads_the_versioned_contract():
    contract = _contract()
    assert contract["contract_id"] == "uci_credit_default_benchmark_v1"
    assert len(contract["task"]["features"]) == 23


def test_frame_validation_passes_for_contract_consistent_data():
    contract = _contract()
    contract["data_expectations"]["rows"] = 2
    report = validate_uci_benchmark_frame(_small_frame(contract), contract)
    assert report["passed"] is True
    assert report["feature_count"] == 23
    assert report["training_performed"] is False


def test_frame_validation_rejects_duplicate_identifiers():
    contract = _contract()
    contract["data_expectations"]["rows"] = 2
    frame = _small_frame(contract)
    frame["ID"] = [101, 101]
    report = validate_uci_benchmark_frame(frame, contract)
    assert report["passed"] is False
    assert any("duplicates" in error for error in report["errors"])


def test_frame_validation_rejects_invalid_target_values():
    contract = _contract()
    contract["data_expectations"]["rows"] = 2
    frame = _small_frame(contract)
    frame["default payment next month"] = [0, 2]
    report = validate_uci_benchmark_frame(frame, contract)
    assert report["passed"] is False
    assert any("Target column" in error for error in report["errors"])


def test_frame_validation_rejects_missing_values():
    contract = _contract()
    contract["data_expectations"]["rows"] = 2
    frame = _small_frame(contract)
    frame.loc[0, "AGE"] = None
    report = validate_uci_benchmark_frame(frame, contract)
    assert report["passed"] is False
    assert any("Missing values" in error for error in report["errors"])


def test_contract_path_cannot_escape_project_root(tmp_path):
    with pytest.raises(DataContractError):
        load_uci_benchmark_contract(tmp_path, "../../outside.json")
