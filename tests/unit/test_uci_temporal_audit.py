import json
from pathlib import Path

import pandas as pd
import pytest

from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import load_uci_benchmark_contract
from cci.data.uci_temporal_audit import (
    audit_uci_temporal_availability,
    load_uci_temporal_config,
)


ROOT = Path(__file__).resolve().parents[2]


def _frame():
    contract = load_uci_benchmark_contract(ROOT)
    columns = contract["data_expectations"]["column_names"]
    rows = []
    for index, target in enumerate([0, 1, 0, 1]):
        row = {column: index + 1 for column in columns}
        row["ID"] = 100 + index
        row["default payment next month"] = target
        rows.append(row)
    return pd.DataFrame(rows), contract


def test_temporal_audit_is_json_serializable_and_keeps_all_availability_unresolved():
    frame, contract = _frame()
    config = load_uci_temporal_config(ROOT)
    report = audit_uci_temporal_availability(frame, ROOT, contract, config)

    assert report["rows"] == 4
    assert report["feature_count"] == 23
    assert report["identifier_excluded"] is True
    assert report["target_excluded_from_features"] is True
    assert report["availability_summary"] == {
        "certified_available_at_operational_cutoff": 0,
        "unresolved": 23,
        "all_features_certified_available": False,
    }
    assert report["source_temporal_scope"]["latest_documented_predictor_month"] == "2005-09"
    assert report["source_temporal_scope"]["exact_operational_observation_cutoff"] is None
    assert report["target_temporal_assessment"]["calendar_window"] is None
    assert report["leakage_assessment"]["status"] == "not_determined"
    assert report["training_authorized"] is False
    assert report["preprocessing_fitted"] is False
    assert report["frame_modified"] is False
    json.dumps(report)


def test_monthly_feature_mapping_matches_documented_calendar_months():
    frame, contract = _frame()
    report = audit_uci_temporal_availability(frame, ROOT, contract)

    assert set(report["monthly_feature_groups"]["2005-09"]) == {
        "PAY_0", "BILL_AMT1", "PAY_AMT1"
    }
    assert set(report["monthly_feature_groups"]["2005-04"]) == {
        "PAY_6", "BILL_AMT6", "PAY_AMT6"
    }
    assert report["field_audit"]["PAY_0"]["availability_at_operational_cutoff"] == "unresolved"
    assert report["field_audit"]["PAY_0"]["potential_leakage_status"] == "not_determined"
    assert report["field_audit"]["LIMIT_BAL"]["reference_period_status"] == "reference_date_not_documented"


def test_temporal_audit_does_not_mutate_frame():
    frame, contract = _frame()
    before = frame.copy(deep=True)

    audit_uci_temporal_availability(frame, ROOT, contract)

    pd.testing.assert_frame_equal(frame, before)


def test_temporal_audit_rejects_schema_drift():
    frame, contract = _frame()
    frame = frame.drop(columns=["PAY_0"])

    with pytest.raises(DataContractError):
        audit_uci_temporal_availability(frame, ROOT, contract)


def test_temporal_audit_rejects_incomplete_feature_metadata():
    frame, contract = _frame()
    config = load_uci_temporal_config(ROOT)
    config["feature_temporal_metadata"].pop("PAY_0")

    with pytest.raises(DataContractError):
        audit_uci_temporal_availability(frame, ROOT, contract, config)


def test_temporal_audit_rejects_undocumented_target_calendar_window():
    frame, contract = _frame()
    config = load_uci_temporal_config(ROOT)
    config["target_temporal_metadata"]["calendar_window"] = "2005-10"

    with pytest.raises(DataContractError):
        audit_uci_temporal_availability(frame, ROOT, contract, config)


def test_temporal_config_path_cannot_escape_project_root():
    with pytest.raises(DataContractError):
        load_uci_temporal_config(ROOT, "../outside.json")
