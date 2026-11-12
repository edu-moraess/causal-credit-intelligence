"""Tests for exception hierarchy."""

from __future__ import annotations

import pytest

from cci.core.exceptions import (
    CCIError,
    ConfigError,
    DataContractError,
    ValidationError,
    DataLeakageError,
    ModelNotTrainedError,
)


def test_base_exception():
    err = CCIError("base error", context={"key": "value"})
    assert "base error" in str(err)
    assert err.context["key"] == "value"


def test_inheritance():
    assert issubclass(ConfigError, CCIError)
    assert issubclass(DataContractError, CCIError)
    assert issubclass(ValidationError, CCIError)
    assert issubclass(DataLeakageError, ValidationError)
    assert issubclass(ModelNotTrainedError, CCIError)


def test_raise_and_catch():
    with pytest.raises(DataLeakageError):
        raise DataLeakageError("leak detected")
