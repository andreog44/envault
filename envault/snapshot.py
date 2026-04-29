"""Snapshot management for envault — save and restore vault states."""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_DIR_NAME = ".snapshots"


def get_snapshot_dir(vault_path: Path) -> Path:
    """Return the snapshot directory for a given vault file."""
    return vault_path.parent / SNAPSHOT_DIR_NAME


def list_snapshots(vault_path: Path) -> list[dict]:
    """List all snapshots for a vault, sorted by creation time (newest first)."""
    snap_dir = get_snapshot_dir(vault_path)
    if not snap_dir.exists():
        return []

    manifest_path = snap_dir / "manifest.json"
    if not manifest_path.exists():
        return []

    with open(manifest_path, "r") as f:
        return json.load(f)


def _save_manifest(snap_dir: Path, snapshots: list[dict]) -> None:
    snap_dir.mkdir(parents=True, exist_ok=True)
    with open(snap_dir / "manifest.json", "w") as f:
        json.dump(snapshots, f, indent=2)


def create_snapshot(vault_path: Path, label: str = "") -> dict:
    """Create a snapshot of the current vault file."""
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    snap_dir = get_snapshot_dir(vault_path)
    snap_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    snapshot_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    snap_file = snap_dir / f"{snapshot_id}.vault"

    shutil.copy2(vault_path, snap_file)

    entry = {
        "id": snapshot_id,
        "timestamp": timestamp,
        "label": label,
        "file": snap_file.name,
    }

    snapshots = list_snapshots(vault_path)
    snapshots.insert(0, entry)
    _save_manifest(snap_dir, snapshots)

    return entry


def restore_snapshot(vault_path: Path, snapshot_id: str) -> None:
    """Restore a vault from a snapshot by ID."""
    snapshots = list_snapshots(vault_path)
    match = next((s for s in snapshots if s["id"] == snapshot_id), None)
    if match is None:
        raise ValueError(f"Snapshot not found: {snapshot_id}")

    snap_dir = get_snapshot_dir(vault_path)
    snap_file = snap_dir / match["file"]

    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot file missing: {snap_file}")

    shutil.copy2(snap_file, vault_path)


def delete_snapshot(vault_path: Path, snapshot_id: str) -> None:
    """Delete a snapshot by ID."""
    snapshots = list_snapshots(vault_path)
    match = next((s for s in snapshots if s["id"] == snapshot_id), None)
    if match is None:
        raise ValueError(f"Snapshot not found: {snapshot_id}")

    snap_dir = get_snapshot_dir(vault_path)
    snap_file = snap_dir / match["file"]
    if snap_file.exists():
        snap_file.unlink()

    updated = [s for s in snapshots if s["id"] != snapshot_id]
    _save_manifest(snap_dir, updated)
