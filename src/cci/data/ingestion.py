"""Explicit, read-only ingestion from the project's raw-data directory."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from cci.core.exceptions import DataContractError


def _raw_root(root: str | Path | None = None) -> Path:
    project = Path(root).resolve() if root else Path(__file__).resolve().parents[3]
    return (project / "data" / "raw").resolve()


def list_available_sources(root: str | Path | None = None) -> list[str]:
    directory = _raw_root(root)
    if not directory.exists():
        return []
    return sorted(p.name for p in directory.iterdir() if p.is_file() and p.suffix.lower() in {".csv", ".parquet"})


def load_raw(source: str, root: str | Path | None = None) -> Any:
    """Load CSV/Parquet only from data/raw; never downloads or modifies data."""
    import pandas as pd
    base = _raw_root(root)
    candidate = (base / source).resolve()
    if candidate.parent != base or candidate.suffix.lower() not in {".csv", ".parquet"}:
        raise DataContractError("Source must be a CSV or Parquet file directly under data/raw.")
    if not candidate.is_file():
        raise FileNotFoundError(f"Raw data source not found: {candidate.name}")
    if candidate.suffix.lower() == ".csv":
        return pd.read_csv(candidate)
    return pd.read_parquet(candidate)
