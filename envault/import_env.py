"""Import environment variables from various sources into a vault."""

import os
from pathlib import Path
from typing import Optional

from envault.vault import seal
from envault.export import parse_env_file


def import_from_file(env_file: Path, vault_path: Path, password: str) -> int:
    """Import variables from a .env file into a vault.

    Returns the number of variables imported.
    """
    if not env_file.exists():
        raise FileNotFoundError(f"Source file not found: {env_file}")

    content = env_file.read_text(encoding="utf-8")
    variables = parse_env_file(content)

    if not variables:
        return 0

    lines = [f"{key}={value}" for key, value in variables.items()]
    env_content = "\n".join(lines) + "\n"

    seal(env_content, vault_path, password)
    return len(variables)


def import_from_os_env(
    vault_path: Path,
    password: str,
    prefix: Optional[str] = None,
    keys: Optional[list] = None,
) -> int:
    """Import variables from the current OS environment into a vault.

    Optionally filter by prefix or explicit list of keys.
    Returns the number of variables imported.
    """
    env_vars = dict(os.environ)

    if keys is not None:
        env_vars = {k: v for k, v in env_vars.items() if k in keys}
    elif prefix is not None:
        env_vars = {k: v for k, v in env_vars.items() if k.startswith(prefix)}

    if not env_vars:
        return 0

    lines = [f"{key}={value}" for key, value in env_vars.items()]
    env_content = "\n".join(lines) + "\n"

    seal(env_content, vault_path, password)
    return len(env_vars)


def merge_env_file(env_file: Path, vault_path: Path, password: str, overwrite: bool = False) -> dict:
    """Merge variables from a .env file into an existing vault.

    Returns a dict with 'added' and 'skipped' counts.
    """
    from envault.vault import unseal
    from envault.export import parse_env_file as _parse

    if not env_file.exists():
        raise FileNotFoundError(f"Source file not found: {env_file}")

    incoming = _parse(env_file.read_text(encoding="utf-8"))

    existing = {}
    if vault_path.exists():
        existing_content = unseal(vault_path, password)
        existing = _parse(existing_content)

    added = 0
    skipped = 0
    for key, value in incoming.items():
        if key in existing and not overwrite:
            skipped += 1
        else:
            existing[key] = value
            added += 1

    merged_lines = [f"{k}={v}" for k, v in existing.items()]
    seal("\n".join(merged_lines) + "\n", vault_path, password)

    return {"added": added, "skipped": skipped}
