"""Deterministic hashes and minimal experiment governance records."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def sha256_of_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_of_dict(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return sha256_of_bytes(payload)


@dataclass
class ExperimentRecord:
    experiment_id: str
    status: str
    data_hash: str | None = None
    config_hash: str | None = None
    methodology_ref: str | None = None

    def is_valid_for_reporting(self) -> bool:
        return bool(self.experiment_id and self.status == "completed" and
                    self.data_hash and self.config_hash and self.methodology_ref)


class AuditTrail:
    def __init__(self):
        self._events = []

    def record(self, event_type: str, description: str, **metadata):
        event = {"event_type": event_type, "description": description,
                 "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                 "metadata": metadata}
        self._events.append(event)
        return dict(event)

    def list_events(self):
        return [dict(item) for item in self._events]

    def status(self):
        return {"n_events": len(self._events)}
