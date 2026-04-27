"""Configuration management for envault.

Handles reading and writing of per-project .envault config files
that store metadata such as vault path overrides and default env files.
"""

import json
import os
from pathlib import Path

CONFIG_FILENAME = ".envault.json"
DEFAULT_CONFIG = {
    "vault_dir": ".envault",
    "default_env_file": ".env",
    "created_at": None,
}


def get_config_path(project_dir: str | Path | None = None) -> Path:
    """Return the path to the config file for the given project directory."""
    base = Path(project_dir) if project_dir else Path.cwd()
    return base / CONFIG_FILENAME


def load_config(project_dir: str | Path | None = None) -> dict:
    """Load config from disk, returning defaults if no config file exists."""
    config_path = get_config_path(project_dir)
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
    with config_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    # Merge with defaults so new keys are always present
    merged = DEFAULT_CONFIG.copy()
    merged.update(data)
    return merged


def save_config(config: dict, project_dir: str | Path | None = None) -> Path:
    """Persist *config* to the project config file and return its path."""
    config_path = get_config_path(project_dir)
    with config_path.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")
    return config_path


def init_config(
    project_dir: str | Path | None = None,
    vault_dir: str = ".envault",
    default_env_file: str = ".env",
) -> dict:
    """Create a fresh config file for a project, returning the config dict."""
    from datetime import datetime, timezone

    config = DEFAULT_CONFIG.copy()
    config["vault_dir"] = vault_dir
    config["default_env_file"] = default_env_file
    config["created_at"] = datetime.now(timezone.utc).isoformat()
    save_config(config, project_dir)
    return config
