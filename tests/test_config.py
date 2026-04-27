"""Tests for envault.config module."""

import json
from pathlib import Path

import pytest

from envault.config import (
    CONFIG_FILENAME,
    DEFAULT_CONFIG,
    get_config_path,
    init_config,
    load_config,
    save_config,
)


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_get_config_path_returns_correct_filename(project_dir):
    path = get_config_path(project_dir)
    assert path == project_dir / CONFIG_FILENAME


def test_load_config_returns_defaults_when_no_file(project_dir):
    config = load_config(project_dir)
    assert config == DEFAULT_CONFIG


def test_save_and_load_roundtrip(project_dir):
    cfg = DEFAULT_CONFIG.copy()
    cfg["vault_dir"] = "custom_vault"
    save_config(cfg, project_dir)
    loaded = load_config(project_dir)
    assert loaded["vault_dir"] == "custom_vault"


def test_save_creates_valid_json(project_dir):
    cfg = DEFAULT_CONFIG.copy()
    save_config(cfg, project_dir)
    raw = (project_dir / CONFIG_FILENAME).read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert isinstance(parsed, dict)


def test_init_config_writes_file(project_dir):
    init_config(project_dir)
    assert (project_dir / CONFIG_FILENAME).exists()


def test_init_config_sets_created_at(project_dir):
    config = init_config(project_dir)
    assert config["created_at"] is not None


def test_init_config_custom_vault_dir(project_dir):
    config = init_config(project_dir, vault_dir="secrets")
    assert config["vault_dir"] == "secrets"
    loaded = load_config(project_dir)
    assert loaded["vault_dir"] == "secrets"


def test_load_config_merges_missing_keys(project_dir):
    # Write a config that is missing the 'default_env_file' key
    partial = {"vault_dir": "partial"}
    (project_dir / CONFIG_FILENAME).write_text(json.dumps(partial), encoding="utf-8")
    loaded = load_config(project_dir)
    assert "default_env_file" in loaded
    assert loaded["vault_dir"] == "partial"
