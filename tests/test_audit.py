"""Tests for envault.audit module."""

import json
import pytest
from pathlib import Path

from envault.audit import (
    get_audit_path,
    load_audit_log,
    save_audit_log,
    record_event,
    clear_audit_log,
    AUDIT_FILENAME,
)


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def test_get_audit_path_returns_correct_filename(project_dir):
    path = get_audit_path(project_dir)
    assert path.name == AUDIT_FILENAME
    assert path.parent == Path(project_dir)


def test_load_audit_log_returns_empty_when_no_file(project_dir):
    entries = load_audit_log(project_dir)
    assert entries == []


def test_save_and_load_roundtrip(project_dir):
    entries = [{"action": "lock", "timestamp": "2024-01-01T00:00:00+00:00"}]
    save_audit_log(project_dir, entries)
    loaded = load_audit_log(project_dir)
    assert loaded == entries


def test_record_event_creates_entry(project_dir):
    entry = record_event(project_dir, action="lock", profile="production")
    assert entry["action"] == "lock"
    assert entry["profile"] == "production"
    assert "timestamp" in entry
    assert "user" in entry


def test_record_event_appends_to_log(project_dir):
    record_event(project_dir, action="lock")
    record_event(project_dir, action="unlock")
    entries = load_audit_log(project_dir)
    assert len(entries) == 2
    assert entries[0]["action"] == "lock"
    assert entries[1]["action"] == "unlock"


def test_record_event_persists_to_disk(project_dir):
    record_event(project_dir, action="rotate", details="password changed")
    audit_path = get_audit_path(project_dir)
    with open(audit_path) as f:
        data = json.load(f)
    assert data[0]["details"] == "password changed"


def test_clear_audit_log_removes_all_entries(project_dir):
    record_event(project_dir, action="lock")
    record_event(project_dir, action="unlock")
    clear_audit_log(project_dir)
    assert load_audit_log(project_dir) == []


def test_record_event_no_profile_is_none(project_dir):
    entry = record_event(project_dir, action="init")
    assert entry["profile"] is None
