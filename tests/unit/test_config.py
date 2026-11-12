"""Tests for configuration loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from cci.core.config import get_config, clear_config_cache, get_project_root, Config
from cci.core.exceptions import ConfigError


def test_project_root_exists(project_root: Path):
    root = get_project_root()
    assert root.exists()
    assert (root / "configs").is_dir() or (project_root / "configs").is_dir()


def test_load_app_config():
    clear_config_cache()
    cfg = get_config("app")
    assert isinstance(cfg, Config)
    assert cfg.get("app.name") is not None or cfg.get("app") is not None
    name = cfg.get("app.name")
    assert name == "Causal Credit Intelligence" or name is None


def test_load_data_config():
    clear_config_cache()
    cfg = get_config("data")
    assert isinstance(cfg, Config)
    data = cfg.get("data")
    assert data is not None or cfg.get("contract") is not None


def test_load_model_config():
    clear_config_cache()
    cfg = get_config("model")
    assert isinstance(cfg, Config)


def test_missing_config_raises():
    clear_config_cache()
    with pytest.raises(ConfigError):
        get_config("nonexistent_config_xyz")


def test_config_to_dict():
    clear_config_cache()
    cfg = get_config("app")
    d = cfg.to_dict()
    assert isinstance(d, dict)
