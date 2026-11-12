"""Causal forest estimator interface (foundation stub)."""
class CausalForestEstimator:
    def __init__(self, config=None):
        self.config = config or {}
        self.is_fitted = False

    def fit(self, X, treatment, outcome, **kwargs):
        raise NotImplementedError("Causal forest is not implemented; no causal model has been fitted.")

    def effect(self, X):
        if not self.is_fitted:
            from cci.core.exceptions import ModelNotTrainedError
            raise ModelNotTrainedError("Causal forest estimator has not been fitted.")
        raise NotImplementedError
