"""
Pytest configuration and shared fixtures for CCI foundation tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure src is importable
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


@pytest.fixture(scope="session")
def project_root() -> Path:
    return _ROOT


@pytest.fixture(scope="session")
def src_path() -> Path:
    return _SRC
