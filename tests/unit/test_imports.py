"""Verify that all foundation modules import cleanly."""

from __future__ import annotations


def test_import_cci_package():
    import cci
    assert hasattr(cci, "__version__")
    assert cci.__version__ == "0.1.0"


def test_import_core():
    from cci.core import config, exceptions, logging  # noqa: F401
    from cci.core.config import get_config, Config
    from cci.core.exceptions import CCIError, ConfigError, DataContractError
    from cci.core.logging import get_logger, setup_logging
    assert callable(get_config)
    assert callable(get_logger)


def test_import_data():
    from cci.data import contracts, validation, ingestion  # noqa: F401
    from cci.data.contracts import DataContract
    from cci.data.validation import ValidationReport, run_structural_validation
    assert DataContract is not None


def test_import_features():
    from cci.features.engineering import FeaturePipeline
    assert FeaturePipeline is not None


def test_import_models():
    from cci.models.pd_model import PDModel
    from cci.models.double_ml import DoubleMLEstimator
    from cci.models.causal_forest import CausalForestEstimator
    assert PDModel is not None
    assert DoubleMLEstimator is not None
    assert CausalForestEstimator is not None


def test_import_evaluation():
    from cci.evaluation.metrics import MetricsRegistry
    from cci.evaluation.diagnostics import DiagnosticsReport
    assert MetricsRegistry is not None


def test_import_simulation():
    from cci.simulation.scenarios import ScenarioSimulator
    assert ScenarioSimulator is not None


def test_import_reporting():
    from cci.reporting.reports import AuditTrail, ExperimentRecord, sha256_of_dict
    assert callable(sha256_of_dict)
