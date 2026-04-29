"""Diff utilities for comparing vault contents across profiles or versions."""

from pathlib import Path
from typing import Optional

from envault.export import parse_env_file
from envault.vault import unseal


def load_env_vars(vault_path: Path, password: str) -> dict:
    """Decrypt a vault and return its key-value pairs."""
    content = unseal(vault_path, password)
    return parse_env_file(content)


def diff_vaults(
    vault_a: Path,
    password_a: str,
    vault_b: Path,
    password_b: Optional[str] = None,
) -> dict:
    """Compare two vault files and return a diff summary.

    Returns a dict with:
      - 'added':   keys present in b but not a
      - 'removed': keys present in a but not b
      - 'changed': keys present in both but with different values
      - 'unchanged': keys with identical values in both
    """
    if password_b is None:
        password_b = password_a

    vars_a = load_env_vars(vault_a, password_a)
    vars_b = load_env_vars(vault_b, password_b)

    keys_a = set(vars_a)
    keys_b = set(vars_b)

    added = {k: vars_b[k] for k in keys_b - keys_a}
    removed = {k: vars_a[k] for k in keys_a - keys_b}
    changed = {
        k: {"old": vars_a[k], "new": vars_b[k]}
        for k in keys_a & keys_b
        if vars_a[k] != vars_b[k]
    }
    unchanged = {
        k: vars_a[k]
        for k in keys_a & keys_b
        if vars_a[k] == vars_b[k]
    }

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def format_diff(diff: dict, hide_values: bool = False) -> str:
    """Render a diff dict as a human-readable string."""
    lines = []

    for key, value in sorted(diff["added"].items()):
        display = "***" if hide_values else value
        lines.append(f"+ {key}={display}")

    for key, value in sorted(diff["removed"].items()):
        display = "***" if hide_values else value
        lines.append(f"- {key}={display}")

    for key, vals in sorted(diff["changed"].items()):
        if hide_values:
            lines.append(f"~ {key}=*** -> ***")
        else:
            lines.append(f"~ {key}={vals['old']} -> {vals['new']}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)
