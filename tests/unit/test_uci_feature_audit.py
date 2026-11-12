from pathlib import Path

import pandas as pd
import pytest

from cci.core.exceptions import DataContractError
from cci.data.uci_benchmark import load_uci_benchmark_contract
from cci.data.uci_feature_audit import audit_uci_feature_readiness


ROOT = Path(__file__).resolve().parents[2]


def _frame():
    contract = load_uci_benchmark_contract(ROOT)
    columns = contract["data_expectations"]["column_names"]
    rows = []
    for index, target in enumerate([0, 1, 0, 1]):
        row = {column: index + 1 for column in columns}
        row["ID"] = 100 + index
        row["SEX"] = 1 + (index % 2)
        row["EDUCATION"] = [1, 2, 5, 6][index]
        row["MARRIAGE"] = [1, 2, 0, 3][index]
        row["default payment next month"] = target
        rows.append(row)
    return pd.DataFrame(rows), contract


def test_feature_readiness_audit_is_json_serializable_and_scope_limited():
    frame, contract = _frame()
    report = audit_uci_feature_readiness(frame, ROOT, contract)
    assert report["rows"] == 4
    assert report["feature_count"] == 23
    assert report["identifier_excluded"] is True
    assert report["target_excluded_from_features"] is True
    assert report["training_performed"] is False
    assert report["transformations_fitted"] is False
    assert report["formal_fairness_metrics_computed"] is False
    assert report["feature_availability"]["status"] == "unresolved"
    assert report["columns"]["EDUCATION"]["observed_value_counts"]["5"] == 1
    assert report["columns"]["EDUCATION"]["semantic_relabeling_performed"] is False


def test_feature_readiness_audit_does_not_mutate_frame():
    frame, contract = _frame()
    before = frame.copy(deep=True)
    audit_uci_feature_readiness(frame, ROOT, contract)
    pd.testing.assert_frame_equal(frame, before)


def test_feature_readiness_audit_rejects_schema_drift():
    frame, contract = _frame()
    frame = frame.drop(columns=["PAY_0"])
    with pytest.raises(DataContractError):
        audit_uci_feature_readiness(frame, ROOT, contract)


def test_feature_readiness_audit_rejects_missing_target():
    frame, contract = _frame()
    frame.loc[0, "default payment next month"] = None
    with pytest.raises(DataContractError):
        audit_uci_feature_readiness(frame, ROOT, contract)
