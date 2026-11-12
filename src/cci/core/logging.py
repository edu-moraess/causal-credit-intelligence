"""
Centralized logging configuration for CCI.

Provides structured, consistent logging across all modules.
Compatible with both local execution and Google Colab environments.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

_CONFIGURED = False
_DEFAULT_LEVEL = logging.INFO
_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: int | str = _DEFAULT_LEVEL,
    stream: Optional[object] = None,
) -> None:
    """
    Configure root logger for the CCI platform.

    Safe to call multiple times; subsequent calls update the level only.
    """
    global _CONFIGURED

    if isinstance(level, str):
        level = getattr(logging, level.upper(), _DEFAULT_LEVEL)

    root = logging.getLogger("cci")
    root.setLevel(level)

    if not _CONFIGURED:
        handler = logging.StreamHandler(stream or sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        root.addHandler(handler)
        root.propagate = False
        _CONFIGURED = True
    else:
        for handler in root.handlers:
            handler.setLevel(level)


def get_logger(name: str = "cci") -> logging.Logger:
    """
    Return a named logger under the cci hierarchy.

    Ensures logging is initialized with default settings if not yet configured.
    """
    if not _CONFIGURED:
        setup_logging()
    if not name.startswith("cci"):
        name = f"cci.{name}"
    return logging.getLogger(name)
