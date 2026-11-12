"""Feature preparation contracts; no automatic feature selection or fitting."""
from __future__ import annotations


class FeaturePipeline:
    def __init__(self, covariates: list[str] | tuple[str, ...] | None = None):
        self.covariates = tuple(covariates or ())

    def transform(self, frame):
        missing = sorted(set(self.covariates) - set(frame.columns))
        if missing:
            raise ValueError(f"Missing configured covariates: {missing}")
        return frame.loc[:, list(self.covariates)].copy()
