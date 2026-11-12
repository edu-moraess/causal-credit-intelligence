"""Read-only loader and structural validator for the UCI PD benchmark.

This adapter is separate from the CCI causal-data ingestion path. It verifies
provenance and reads the original XLS member in memory; it never extracts,
downloads, normalizes, or modifies the raw archive.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

from cci.core.exceptions import DataContractError


DEFAULT_CONTRACT = Path("configs/datasets/uci_credit_default_benchmark_v1.json")


def _project_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parents[3]


def load_uci_benchmark_contract(
    root: str | Path | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT,
) -> dict[str, Any]:
    """Load the versioned benchmark contract from the project directory."""
    project = _project_root(root)
    path = (project / contract_path).resolve()
    if not path.is_relative_to(project):
        raise DataContractError("Contract path must remain inside the project root.")
    if not path.is_file():
        raise FileNotFoundError(f"UCI benchmark contract not found: {path}")
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataContractError(f"Unable to read UCI benchmark contract: {exc}") from exc
    if contract.get("contract_id") != "uci_credit_default_benchmark_v1":
        raise DataContractError("Unexpected UCI benchmark contract identifier.")
    return contract


def _read_verified_xls_bytes(root: str | Path, contract: dict[str, Any]) -> bytes:
    project = _project_root(root)
    source = contract["source"]
    archive_path = (project / source["archive_path"]).resolve()
    if not archive_path.is_relative_to(project):
        raise DataContractError("Archive path must remain inside the project root.")
    if not archive_path.is_file():
        raise FileNotFoundError(f"UCI source archive not found: {archive_path}")

    archive_bytes = archive_path.read_bytes()
    digest = hashlib.sha256(archive_bytes).hexdigest()
    expected_digest = source["archive_sha256"]
    if digest != expected_digest:
        raise DataContractError(
            "UCI archive SHA-256 mismatch.",
            context={"expected": expected_digest, "actual": digest},
        )

    expected_member = source["source_member"]
    try:
        with zipfile.ZipFile(BytesIO(archive_bytes), "r") as archive:
            if archive.testzip() is not None:
                raise DataContractError("UCI ZIP archive failed its CRC integrity check.")
            members = [name for name in archive.namelist() if not name.endswith("/")]
            if members != [expected_member]:
                raise DataContractError(
                    "Unexpected UCI archive contents.",
                    context={"expected": [expected_member], "actual": members},
                )
            return archive.read(expected_member)
    except zipfile.BadZipFile as exc:
        raise DataContractError("UCI source is not a valid ZIP archive.") from exc


def validate_uci_benchmark_frame(
    frame: Any,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a loaded frame against the source-specific benchmark contract."""
    if contract is None:
        contract = load_uci_benchmark_contract()

    expected = contract["data_expectations"]
    task = contract["task"]
    identifier = contract["identifier"]["column"]
    target = task["target"]
    errors: list[str] = []

    if list(frame.columns) != expected["column_names"]:
        errors.append("Column names or order do not match the benchmark contract.")
    if len(frame) != expected["rows"]:
        errors.append(f"Expected {expected['rows']} rows; received {len(frame)}.")
    if len(frame.columns) != expected["columns"]:
        errors.append(
            f"Expected {expected['columns']} columns; received {len(frame.columns)}."
        )
    if bool(frame.isna().to_numpy().any()) and not expected["missing_values_allowed"]:
        errors.append("Missing values are not allowed by the benchmark contract.")
    if identifier not in frame.columns or frame[identifier].isna().any():
        errors.append(f"Identifier column {identifier!r} is missing or contains nulls.")
    elif not frame[identifier].is_unique and not expected["duplicate_ids_allowed"]:
        errors.append(f"Identifier column {identifier!r} contains duplicates.")
    if target not in frame.columns:
        errors.append(f"Target column {target!r} is missing.")
    elif not set(frame[target].dropna().unique().tolist()).issubset(
        set(task["allowed_target_values"])
    ) or frame[target].isna().any():
        errors.append(f"Target column {target!r} contains invalid or missing values.")
    if expected["all_columns_numeric"]:
        import pandas as pd

        non_numeric = [
            str(column)
            for column in frame.columns
            if not pd.api.types.is_numeric_dtype(frame[column])
        ]
        if non_numeric:
            errors.append(f"Non-numeric columns found: {non_numeric}")

    return {
        "passed": not errors,
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "feature_count": len(task["features"]),
        "errors": errors,
        "training_performed": False,
        "source_modified": False,
    }


def load_uci_default_benchmark(
    root: str | Path | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT,
):
    """Load the UCI XLS member in memory after provenance and schema checks.

    Requires the optional xlrd dependency. The source ZIP is never extracted
    or modified. Returns the validated pandas DataFrame.
    """
    import pandas as pd

    project = _project_root(root)
    contract = load_uci_benchmark_contract(project, contract_path)
    xls_bytes = _read_verified_xls_bytes(project, contract)
    try:
        frame = pd.read_excel(
            BytesIO(xls_bytes),
            sheet_name=contract["source"]["sheet_name"],
            header=contract["source"]["pandas_header_index"],
            engine="xlrd",
        )
    except ImportError as exc:
        raise DataContractError(
            "Reading the UCI XLS requires the optional dependency xlrd. "
            "Install with: pip install '.[benchmark]'"
        ) from exc

    report = validate_uci_benchmark_frame(frame, contract)
    if not report["passed"]:
        raise DataContractError(
            "UCI benchmark frame failed validation.",
            context={"errors": report["errors"]},
        )
    return frame
