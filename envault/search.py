"""Search for keys across vault files in a project."""

import re
from pathlib import Path
from typing import Optional

from envault.vault import get_vault_path, unseal
from envault.export import parse_env_file


def search_keys(
    project_dir: Path,
    pattern: str,
    password: str,
    profile: Optional[str] = None,
    case_sensitive: bool = False,
) -> list[dict]:
    """Search for keys matching a pattern in the decrypted vault.

    Returns a list of match dicts with 'key', 'value', and 'vault' fields.
    """
    vault_path = get_vault_path(project_dir, profile=profile)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    plaintext = unseal(vault_path, password)
    env_vars = parse_env_file(plaintext)

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern '{pattern}': {exc}") from exc

    matches = []
    for key, value in env_vars.items():
        if compiled.search(key):
            matches.append({
                "key": key,
                "value": value,
                "vault": str(vault_path),
            })

    return matches


def search_values(
    project_dir: Path,
    pattern: str,
    password: str,
    profile: Optional[str] = None,
    case_sensitive: bool = False,
) -> list[dict]:
    """Search for keys whose values match a pattern in the decrypted vault.

    Returns a list of match dicts with 'key', 'value', and 'vault' fields.
    """
    vault_path = get_vault_path(project_dir, profile=profile)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    plaintext = unseal(vault_path, password)
    env_vars = parse_env_file(plaintext)

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern '{pattern}': {exc}") from exc

    matches = []
    for key, value in env_vars.items():
        if compiled.search(value):
            matches.append({
                "key": key,
                "value": value,
                "vault": str(vault_path),
            })

    return matches
