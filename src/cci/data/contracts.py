"""Versioned data contracts for credit-risk observational datasets.

The contract describes columns and temporal roles; it does not assert that
any supplied dataset satisfies causal-identification assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

REQUIRED_IDENTIFIERS = ("customer_id", "observation_date")
FINANCIAL_VARS = ("credit_limit_before", "credit_limit_after")
HISTORY_VARS = ()
TREATMENT_VARS = ("treatment_indicator",)
OUTCOME_VARS = ("default_6m", "default_12m")
ALL_CONTRACT_FIELDS = tuple(dict.fromkeys(
    REQUIRED_IDENTIFIERS + FINANCIAL_VARS + HISTORY_VARS + TREATMENT_VARS + OUTCOME_VARS
))


@dataclass(frozen=True)
class DataContract:
    name: str = "cci_credit_risk_v1"
    version: str = "0.1.0"
    identifiers: tuple[str, ...] = REQUIRED_IDENTIFIERS
    treatment: str = "treatment_indicator"
    outcomes: tuple[str, ...] = OUTCOME_VARS
    pre_treatment_covariates: tuple[str, ...] = field(default_factory=tuple)
    post_treatment_fields: tuple[str, ...] = ("credit_limit_after", "default_6m", "default_12m")

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "DataContract":
        cfg = raw.get("data", raw)
        treatment = cfg.get("treatment", {})
        outcomes = cfg.get("outcomes", {})
        guard = cfg.get("leakage_guard", {})
        return cls(
            name=cfg.get("contract", "cci_credit_risk_v1"),
            version=cfg.get("contract_version", "0.1.0"),
            identifiers=tuple(cfg.get("identifiers", REQUIRED_IDENTIFIERS)),
            treatment=treatment.get("indicator", "treatment_indicator"),
            outcomes=tuple(x for x in (outcomes.get("primary"), outcomes.get("secondary")) if x),
            pre_treatment_covariates=tuple(cfg.get("pre_treatment_covariates", ())),
            post_treatment_fields=tuple(guard.get("post_treatment_fields", cls.post_treatment_fields)),
        )

    def required_columns(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(self.identifiers + (self.treatment,) + self.outcomes))
