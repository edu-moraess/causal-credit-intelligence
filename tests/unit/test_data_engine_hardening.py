"""Regression tests for YAML-driven data-contract hardening."""
import pandas as pd

from cci.data.contracts import DataContract
from cci.data.validation import run_structural_validation


def _config():
    return {
        "data": {
            "contract": "cci_credit_risk_v1",
            "contract_version": "0.1.0",
            "identifiers": ["customer_id", "observation_date"],
            "treatment": {
                "indicator": "treated",
                "before": "limit_before",
                "after": "limit_after",
            },
            "outcomes": {"primary": "default_6m", "secondary": "default_12m"},
            "pre_treatment_covariates": ["age", "income"],
            "validation": {
                "require_identifiers": True,
                "high_missing_threshold": 0.25,
                "check_duplicates_on": ["customer_id", "observation_date"],
                "enforce_pre_treatment_covariates": True,
            },
            "leakage_guard": {"post_treatment_fields": ["limit_after", "default_6m", "default_12m"]},
        }
    }


def _frame():
    return pd.DataFrame({
        "customer_id": [1, 2, 3],
        "observation_date": ["2025-01-01", "2025-01-02", "2025-01-03"],
        "treated": [0, 1, 0],
        "limit_before": [1000, 1000, 1500],
        "limit_after": [1000, 1500, 1500],
        "default_6m": [0, 0, 1],
        "default_12m": [0, 0, 1],
        "age": [30, 40, 50],
        "income": [3000, 4000, 5000],
    })


def test_contract_reads_treatment_amount_columns_and_validation_settings():
    contract = DataContract.from_mapping(_config())
    assert contract.treatment_before == "limit_before"
    assert contract.treatment_after == "limit_after"
    assert contract.high_missing_threshold == 0.25
    assert contract.duplicate_key == ("customer_id", "observation_date")
    assert "limit_before" in contract.required_columns()
    assert "limit_after" in contract.required_columns()


def test_validation_uses_configured_missingness_threshold():
    contract = DataContract.from_mapping(_config())
    frame = _frame()
    frame.loc[0, "income"] = None
    report = run_structural_validation(frame, contract)
    assert not report.passed
    assert any("income: missingness 0.333 exceeds 0.250" in error for error in report.errors)


def test_validation_uses_configured_duplicate_key():
    contract = DataContract.from_mapping(_config())
    frame = _frame()
    frame.loc[1, "customer_id"] = 1
    frame.loc[1, "observation_date"] = "2025-01-01"
    report = run_structural_validation(frame, contract)
    assert not report.passed
    assert any("duplicate keys" in error for error in report.errors)


def test_binary_treatment_and_outcomes_reject_invalid_values():
    contract = DataContract.from_mapping(_config())
    frame = _frame()
    frame.loc[0, "treated"] = 2
    report = run_structural_validation(frame, contract)
    assert not report.passed
    assert any("treated: expected only 0/1" in error for error in report.errors)


def test_missing_required_columns_short_circuit_dependent_checks():
    contract = DataContract.from_mapping(_config())
    frame = _frame().drop(columns=["limit_after"])
    report = run_structural_validation(frame, contract)
    assert not report.passed
    assert len(report.checks) == 1
    assert "limit_after" in report.errors[0]


def test_pre_treatment_covariates_are_checked_for_leakage():
    raw = _config()
    raw["data"]["pre_treatment_covariates"] = ["age", "limit_after"]
    contract = DataContract.from_mapping(raw)
    report = run_structural_validation(_frame(), contract)
    assert not report.passed
    assert any("Forbidden post-treatment fields" in error for error in report.errors)


def test_missing_pre_treatment_covariates_warns_without_claiming_causal_readiness():
    raw = _config()
    raw["data"].pop("pre_treatment_covariates")
    contract = DataContract.from_mapping(raw)
    report = run_structural_validation(_frame(), contract)
    assert report.passed
    assert any("causal analysis is not ready" in warning for warning in report.warnings)
