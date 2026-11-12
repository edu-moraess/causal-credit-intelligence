"""Tests that model stubs behave correctly (not implemented)."""

from __future__ import annotations

import pytest

from cci.core.exceptions import ModelNotTrainedError
from cci.models.pd_model import PDModel
from cci.models.double_ml import DoubleMLEstimator
from cci.models.causal_forest import CausalForestEstimator
from cci.simulation.scenarios import ScenarioSimulator


def test_pd_model_not_trained():
    m = PDModel()
    assert m.is_trained is False
    status = m.status()
    assert status["is_trained"] is False
    with pytest.raises(NotImplementedError):
        m.fit(None, None)
    with pytest.raises(ModelNotTrainedError):
        m.predict_proba(None)


def test_double_ml_not_fitted():
    m = DoubleMLEstimator()
    assert m.is_fitted is False
    with pytest.raises(NotImplementedError):
        m.fit(None, None, None)
    with pytest.raises(ModelNotTrainedError):
        m.ate()


def test_causal_forest_not_fitted():
    m = CausalForestEstimator()
    assert m.is_fitted is False
    with pytest.raises(NotImplementedError):
        m.fit(None, None, None)


def test_simulator_not_ready():
    s = ScenarioSimulator()
    status = s.status()
    assert status["ready"] is False
    with pytest.raises(NotImplementedError):
        s.run({})
