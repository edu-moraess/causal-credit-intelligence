"""
Standardized exception hierarchy for Causal Credit Intelligence.

All domain exceptions inherit from CCIError to enable consistent
error handling across data, models, evaluation and interface layers.
"""

from __future__ import annotations


class CCIError(Exception):
    """Base exception for all CCI platform errors."""

    def __init__(self, message: str, *, context: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        if self.context:
            ctx = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            return f"{self.message} | context: {ctx}"
        return self.message


class ConfigError(CCIError):
    """Raised when configuration loading or validation fails."""


class DataContractError(CCIError):
    """Raised when a data contract is violated (schema, types, required fields)."""


class ValidationError(CCIError):
    """Raised when structural, temporal or business validation fails."""


class DataLeakageError(ValidationError):
    """
    Raised when potential post-treatment leakage is detected.

    Critical for causal inference integrity: covariates used for
    identification must be measured before the treatment assignment.
    """


class ModelNotTrainedError(CCIError):
    """Raised when inference or evaluation is requested on an untrained model."""


class ExperimentNotFoundError(CCIError):
    """Raised when a requested experiment artifact cannot be located."""


class GovernanceError(CCIError):
    """Raised when governance, versioning or audit constraints are violated."""
