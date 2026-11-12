"""Focused tests for the recovered structural data contracts."""
from cci.data.contracts import DataContract
from cci.data.validation import (
    check_duplicates, check_leakage, run_structural_validation, validate_schema,
)


def test_contract_from_config_shape():
    contract = DataContract()
    assert "customer_id" in contract.required_columns()
    assert "treatment_indicator" in contract.required_columns()


def test_schema_reports_missing_columns():
    report = validate_schema([], ["customer_id"])
    assert report.passed is False


def test_leakage_guard_rejects_post_treatment_covariate():
    report = check_leakage(["age", "credit_limit_after"], ["credit_limit_after"])
    assert report.passed is False


def test_duplicate_check_is_explicit():
    import pandas as pd
    frame = pd.DataFrame({"customer_id": [1, 1], "observation_date": ["2025-01-01", "2025-01-01"]})
    assert check_duplicates(frame).passed is False
