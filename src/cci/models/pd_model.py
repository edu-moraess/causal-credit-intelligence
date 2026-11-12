"""
Probability of Default (PD) model interface.

Foundation only: no training, no inference, no metrics.
Defines the contract that future PD engines must satisfy.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from cci.core.exceptions import ModelNotTrainedError
from cci.core.logging import get_logger

logger = get_logger("models.pd_model")


class PDModel:
    """
    Stub for Probability of Default modelling.

    Future implementations may wrap logistic regression, XGBoost,
    neural nets or scorecard pipelines. Governance requires that
    any trained artifact be registered with data hash, config and
    evaluation metrics before being considered production-ready.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self._is_trained = False
        self.model_id: Optional[str] = None

    def fit(self, X: Any, y: Any, **kwargs: Any) -> "PDModel":
        """Training is not implemented in the foundation stage."""
        raise NotImplementedError(
            "PDModel.fit is not implemented in the foundation stage. "
            "See DEVELOPMENT_ROADMAP.md — PD Engine phase."
        )

    def predict_proba(self, X: Any) -> Any:
        if not self._is_trained:
            raise ModelNotTrainedError(
                "PD model has not been trained. Model not trained."
            )
        raise NotImplementedError("predict_proba not implemented in foundation.")

    def predict(self, X: Any) -> Any:
        if not self._is_trained:
            raise ModelNotTrainedError("PD model has not been trained.")
        raise NotImplementedError("predict not implemented in foundation.")

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def status(self) -> Dict[str, Any]:
        return {
            "component": "PDModel",
            "status": "not_trained",
            "message": "Model not trained. Foundation stage only.",
            "is_trained": False,
        }
