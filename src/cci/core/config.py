"""
Configuration management for Causal Credit Intelligence.

Loads YAML configuration files from the configs/ directory and exposes
a typed, hierarchical Config object. Designed to be Colab-compatible
and free of heavy external dependencies beyond PyYAML.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from cci.core.exceptions import ConfigError
from cci.core.logging import get_logger

logger = get_logger("core.config")

# Project root resolution: works both in package install and source layout
_DEFAULT_ROOT = Path(__file__).resolve().parents[3]


def _find_project_root() -> Path:
    """Locate project root by walking up until configs/ or pyproject.toml is found."""
    candidates = [
        Path.cwd(),
        _DEFAULT_ROOT,
        Path(__file__).resolve().parents[2],  # src/
        Path(__file__).resolve().parents[3],  # project root from package
    ]
    for base in candidates:
        if (base / "configs").is_dir() or (base / "pyproject.toml").exists():
            return base
        # Try parent
        parent = base.parent
        if (parent / "configs").is_dir():
            return parent
    return _DEFAULT_ROOT


class Config:
    """
    Hierarchical configuration container.

    Supports attribute and dict-style access.
    """

    def __init__(self, data: Dict[str, Any], source: Optional[str] = None) -> None:
        self._data = data
        self._source = source

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a top-level or dotted key (e.g. 'data.raw_path')."""
        if "." in key:
            parts = key.split(".")
            node: Any = self._data
            for part in parts:
                if not isinstance(node, dict) or part not in node:
                    return default
                node = node[part]
            return node
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    @property
    def source(self) -> Optional[str]:
        return self._source

    def __repr__(self) -> str:
        return f"Config(source={self._source!r}, keys={list(self._data.keys())})"


_config_cache: Dict[str, Config] = {}


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load a single YAML file. Raises ConfigError on failure."""
    try:
        import yaml
    except ImportError as exc:
        raise ConfigError(
            "PyYAML is required for configuration loading. "
            "Install with: pip install pyyaml"
        ) from exc

    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise ConfigError(f"Configuration root must be a mapping: {path}")
        return data
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc


def get_config(
    name: str = "app",
    *,
    reload: bool = False,
    project_root: Optional[Path] = None,
) -> Config:
    """
    Load and cache a configuration file from configs/{name}.yaml.

    Parameters
    ----------
    name : str
        Configuration name without extension (app, data, model).
    reload : bool
        Force reload from disk, bypassing cache.
    project_root : Path, optional
        Override project root discovery.
    """
    cache_key = name
    if not reload and cache_key in _config_cache:
        return _config_cache[cache_key]

    root = project_root or _find_project_root()
    path = root / "configs" / f"{name}.yaml"

    logger.debug("Loading configuration from %s", path)
    data = load_yaml(path)
    cfg = Config(data, source=str(path))
    _config_cache[cache_key] = cfg
    return cfg


def get_project_root() -> Path:
    """Return the resolved project root directory."""
    return _find_project_root()


def clear_config_cache() -> None:
    """Clear the in-memory configuration cache (useful for tests)."""
    _config_cache.clear()
