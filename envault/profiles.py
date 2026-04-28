"""Profile management for envault — supports multiple named env profiles per project."""

import json
from pathlib import Path
from typing import Optional

from envault.config import load_config, save_config, get_config_path


DEFAULT_PROFILE = "default"


def list_profiles(project_dir: Path) -> list[str]:
    """Return all profile names defined in the project config."""
    config = load_config(project_dir)
    profiles = config.get("profiles", {})
    return list(profiles.keys())


def get_profile(project_dir: Path, name: str) -> Optional[dict]:
    """Return the profile dict for a given name, or None if not found."""
    config = load_config(project_dir)
    return config.get("profiles", {}).get(name)


def add_profile(project_dir: Path, name: str, env_file: str) -> dict:
    """Add or overwrite a named profile with the given env file path."""
    config = load_config(project_dir)
    if "profiles" not in config:
        config["profiles"] = {}
    config["profiles"][name] = {"env_file": env_file}
    save_config(project_dir, config)
    return config["profiles"][name]


def remove_profile(project_dir: Path, name: str) -> bool:
    """Remove a profile by name. Returns True if removed, False if not found."""
    if name == DEFAULT_PROFILE:
        raise ValueError("Cannot remove the default profile.")
    config = load_config(project_dir)
    profiles = config.get("profiles", {})
    if name not in profiles:
        return False
    del profiles[name]
    config["profiles"] = profiles
    save_config(project_dir, config)
    return True


def set_active_profile(project_dir: Path, name: str) -> None:
    """Set the active profile in the project config."""
    config = load_config(project_dir)
    if name not in config.get("profiles", {}):
        raise KeyError(f"Profile '{name}' does not exist.")
    config["active_profile"] = name
    save_config(project_dir, config)


def get_active_profile(project_dir: Path) -> str:
    """Return the currently active profile name, defaulting to 'default'."""
    config = load_config(project_dir)
    return config.get("active_profile", DEFAULT_PROFILE)
