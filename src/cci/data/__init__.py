"""Data layer: ingestion, validation, contracts."""

from cci.data.contracts import (
    DataContract,
    REQUIRED_IDENTIFIERS,
    FINANCIAL_VARS,
    HISTORY_VARS,
    TREATMENT_VARS,
    OUTCOME_VARS,
    ALL_CONTRACT_FIELDS,
)
from cci.data.validation import (
    validate_schema,
    validate_types,
    check_missingness,
    check_duplicates,
    check_temporal_consistency,
    ValidationReport,
)
from cci.data.ingestion import load_raw, list_available_sources

__all__ = [
    "DataContract",
    "REQUIRED_IDENTIFIERS",
    "FINANCIAL_VARS",
    "HISTORY_VARS",
    "TREATMENT_VARS",
    "OUTCOME_VARS",
    "ALL_CONTRACT_FIELDS",
    "validate_schema",
    "validate_types",
    "check_missingness",
    "check_duplicates",
    "check_temporal_consistency",
    "ValidationReport",
    "load_raw",
    "list_available_sources",
]
