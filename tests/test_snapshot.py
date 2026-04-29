"""Tests for envault.snapshot module."""

import pytest
from pathlib import Path

from envault.snapshot import (
    get_snapshot_dir,
    list_snapshots,
    create_snapshot,
    restore_snapshot,
    delete_snapshot,
    SNAPSHOT_DIR_NAME,
)


@pytest.fixture
def vault_file(tmp_path):
    vault = tmp_path / ".vault" / "env.vault"
    vault.parent.mkdir(parents=True)
    vault.write_bytes(b"encrypted-content-v1")
    return vault


def test_get_snapshot_dir_returns_correct_path(vault_file):
    snap_dir = get_snapshot_dir(vault_file)
    assert snap_dir == vault_file.parent / SNAPSHOT_DIR_NAME


def test_list_snapshots_empty_initially(vault_file):
    assert list_snapshots(vault_file) == []


def test_create_snapshot_returns_entry(vault_file):
    entry = create_snapshot(vault_file)
    assert "id" in entry
    assert "timestamp" in entry
    assert "file" in entry
    assert entry["label"] == ""


def test_create_snapshot_with_label(vault_file):
    entry = create_snapshot(vault_file, label="before-deploy")
    assert entry["label"] == "before-deploy"


def test_create_snapshot_appears_in_list(vault_file):
    create_snapshot(vault_file, label="snap1")
    snapshots = list_snapshots(vault_file)
    assert len(snapshots) == 1
    assert snapshots[0]["label"] == "snap1"


def test_create_multiple_snapshots_newest_first(vault_file):
    create_snapshot(vault_file, label="first")
    vault_file.write_bytes(b"encrypted-content-v2")
    create_snapshot(vault_file, label="second")
    snapshots = list_snapshots(vault_file)
    assert len(snapshots) == 2
    assert snapshots[0]["label"] == "second"


def test_create_snapshot_missing_vault_raises(tmp_path):
    missing = tmp_path / ".vault" / "missing.vault"
    with pytest.raises(FileNotFoundError):
        create_snapshot(missing)


def test_restore_snapshot_recovers_content(vault_file):
    original = vault_file.read_bytes()
    entry = create_snapshot(vault_file)
    vault_file.write_bytes(b"overwritten-content")
    restore_snapshot(vault_file, entry["id"])
    assert vault_file.read_bytes() == original


def test_restore_snapshot_invalid_id_raises(vault_file):
    with pytest.raises(ValueError, match="Snapshot not found"):
        restore_snapshot(vault_file, "nonexistent-id")


def test_delete_snapshot_removes_from_list(vault_file):
    entry = create_snapshot(vault_file)
    delete_snapshot(vault_file, entry["id"])
    assert list_snapshots(vault_file) == []


def test_delete_snapshot_removes_file(vault_file):
    entry = create_snapshot(vault_file)
    snap_dir = get_snapshot_dir(vault_file)
    snap_file = snap_dir / entry["file"]
    assert snap_file.exists()
    delete_snapshot(vault_file, entry["id"])
    assert not snap_file.exists()


def test_delete_snapshot_invalid_id_raises(vault_file):
    with pytest.raises(ValueError, match="Snapshot not found"):
        delete_snapshot(vault_file, "bad-id")
