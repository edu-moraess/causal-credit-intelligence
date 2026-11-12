"""Tests for governance reporting utilities."""

from __future__ import annotations

from cci.reporting.reports import (
    AuditTrail,
    ExperimentRecord,
    sha256_of_dict,
    sha256_of_bytes,
)


def test_sha256_deterministic():
    h1 = sha256_of_dict({"a": 1, "b": 2})
    h2 = sha256_of_dict({"b": 2, "a": 1})
    assert h1 == h2
    assert len(h1) == 64


def test_sha256_bytes():
    h = sha256_of_bytes(b"cci-foundation")
    assert len(h) == 64


def test_experiment_record_not_valid_without_hashes():
    rec = ExperimentRecord(experiment_id="exp-001", status="completed")
    assert rec.is_valid_for_reporting() is False

    rec2 = ExperimentRecord(
        experiment_id="exp-002",
        status="completed",
        data_hash="abc",
        config_hash="def",
        methodology_ref="docs/METHODOLOGY.md",
    )
    assert rec2.is_valid_for_reporting() is True


def test_audit_trail():
    trail = AuditTrail()
    event = trail.record("test_event", "unit test")
    assert event["event_type"] == "test_event"
    assert len(trail.list_events()) == 1
    assert trail.status()["n_events"] == 1
