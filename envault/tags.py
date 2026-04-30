"""Tag management for envault vaults.

Allows users to assign and query string tags on vault files,
stored alongside project config.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from envault.config import load_config, save_config


def list_tags(project_dir: Path) -> List[str]:
    """Return all tags assigned to the project vault."""
    config = load_config(project_dir)
    return list(config.get("tags", []))


def add_tag(project_dir: Path, tag: str) -> List[str]:
    """Add a tag to the project vault. Duplicate tags are ignored.

    Returns the updated list of tags.
    """
    tag = tag.strip()
    if not tag:
        raise ValueError("Tag must not be empty.")

    config = load_config(project_dir)
    tags: List[str] = list(config.get("tags", []))

    if tag not in tags:
        tags.append(tag)
        config["tags"] = tags
        save_config(project_dir, config)

    return tags


def remove_tag(project_dir: Path, tag: str) -> List[str]:
    """Remove a tag from the project vault.

    Raises KeyError if the tag does not exist.
    Returns the updated list of tags.
    """
    config = load_config(project_dir)
    tags: List[str] = list(config.get("tags", []))

    if tag not in tags:
        raise KeyError(f"Tag '{tag}' not found.")

    tags.remove(tag)
    config["tags"] = tags
    save_config(project_dir, config)
    return tags


def has_tag(project_dir: Path, tag: str) -> bool:
    """Return True if the project has the given tag."""
    return tag in list_tags(project_dir)


def clear_tags(project_dir: Path) -> None:
    """Remove all tags from the project vault."""
    config = load_config(project_dir)
    config["tags"] = []
    save_config(project_dir, config)
