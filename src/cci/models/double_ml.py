"""Double Machine Learning estimator interface (foundation stub)."""
from cci.core.exceptions import ModelNotTrainedError


class DoubleMLEstimator:
    def __init__(self, config=None):
        self.config = config or {}
        self.is_fitted = False

    def fit(self, X, treatment, outcome, **kwargs):
        raise NotImplementedError("Double ML is not implemented; no causal model has been fitted.")

    def ate(self, *args, **kwargs):
        if not self.is_fitted:
            raise ModelNotTrainedError("Double ML estimator has not been fitted.")
        raise NotImplementedError
