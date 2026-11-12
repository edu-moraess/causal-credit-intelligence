"""Tests for logging setup."""

from __future__ import annotations

import logging

from cci.core.logging import get_logger, setup_logging


def test_get_logger_returns_logger():
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)
    assert logger.name.startswith("cci")


def test_setup_logging_idempotent():
    setup_logging(level="DEBUG")
    setup_logging(level="INFO")
    logger = get_logger("test_idempotent")
    assert logger is not None


def test_logger_hierarchy():
    logger = get_logger("data.validation")
    assert "cci" in logger.name
