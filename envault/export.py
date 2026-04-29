"""Export and import environment variables from/to vault."""

import os
from pathlib import Path
from typing import Optional

from envault.vault import unseal


def parse_env_file(content: str) -> dict:
    """Parse env file content into a dictionary."""
    env_vars = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes if present
        if len(value) >= 2 and value[0] in ('"', "'") and value[0] == value[-1]:
            value = value[1:-1]
        if key:
            env_vars[key] = value
    return env_vars


def export_to_shell(vault_path: Path, password: str) -> str:
    """Decrypt vault and return shell export statements."""
    content = unseal(vault_path, password)
    env_vars = parse_env_file(content)
    lines = [f'export {k}="{v}"' for k, v in env_vars.items()]
    return "\n".join(lines)


def export_to_dict(vault_path: Path, password: str) -> dict:
    """Decrypt vault and return env vars as a dictionary."""
    content = unseal(vault_path, password)
    return parse_env_file(content)


def inject_into_env(vault_path: Path, password: str, overwrite: bool = False) -> dict:
    """Inject decrypted env vars into the current process environment."""
    env_vars = export_to_dict(vault_path, password)
    injected = {}
    for key, value in env_vars.items():
        if overwrite or key not in os.environ:
            os.environ[key] = value
            injected[key] = value
    return injected
