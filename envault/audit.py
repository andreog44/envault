"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_FILENAME = ".envault_audit.json"


def get_audit_path(project_dir: str) -> Path:
    """Return the path to the audit log file for a given project directory."""
    return Path(project_dir) / AUDIT_FILENAME


def load_audit_log(project_dir: str) -> list:
    """Load the audit log entries from disk. Returns empty list if not found."""
    audit_path = get_audit_path(project_dir)
    if not audit_path.exists():
        return []
    with open(audit_path, "r") as f:
        return json.load(f)


def save_audit_log(project_dir: str, entries: list) -> None:
    """Persist audit log entries to disk."""
    audit_path = get_audit_path(project_dir)
    with open(audit_path, "w") as f:
        json.dump(entries, f, indent=2)


def record_event(
    project_dir: str,
    action: str,
    profile: Optional[str] = None,
    details: Optional[str] = None,
) -> dict:
    """Append a new audit event and return the entry."""
    entries = load_audit_log(project_dir)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
        "details": details,
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
    }
    entries.append(entry)
    save_audit_log(project_dir, entries)
    return entry


def clear_audit_log(project_dir: str) -> None:
    """Remove all audit log entries."""
    save_audit_log(project_dir, [])
