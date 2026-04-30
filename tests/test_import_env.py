"""Tests for envault.import_env module."""

import os
import pytest
from pathlib import Path

from envault.import_env import import_from_file, import_from_os_env, merge_env_file
from envault.vault import unseal
from envault.export import parse_env_file


PASSWORD = "test-password-123"


@pytest.fixture
def tmp_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n# comment\nEMPTY=\n")
    return env_file


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / ".vault"


def test_import_from_file_returns_count(tmp_env_file, vault_path):
    count = import_from_file(tmp_env_file, vault_path, PASSWORD)
    assert count == 3  # FOO, BAZ, EMPTY


def test_import_from_file_creates_vault(tmp_env_file, vault_path):
    import_from_file(tmp_env_file, vault_path, PASSWORD)
    assert vault_path.exists()


def test_import_from_file_vault_is_readable(tmp_env_file, vault_path):
    import_from_file(tmp_env_file, vault_path, PASSWORD)
    content = unseal(vault_path, PASSWORD)
    variables = parse_env_file(content)
    assert variables["FOO"] == "bar"
    assert variables["BAZ"] == "qux"


def test_import_from_file_missing_source_raises(tmp_path, vault_path):
    missing = tmp_path / "nonexistent.env"
    with pytest.raises(FileNotFoundError):
        import_from_file(missing, vault_path, PASSWORD)


def test_import_from_os_env_with_prefix(tmp_path, vault_path, monkeypatch):
    monkeypatch.setenv("MYAPP_HOST", "localhost")
    monkeypatch.setenv("MYAPP_PORT", "8080")
    monkeypatch.setenv("OTHER_VAR", "ignored")

    count = import_from_os_env(vault_path, PASSWORD, prefix="MYAPP_")
    assert count == 2

    content = unseal(vault_path, PASSWORD)
    variables = parse_env_file(content)
    assert variables["MYAPP_HOST"] == "localhost"
    assert "OTHER_VAR" not in variables


def test_import_from_os_env_with_keys(tmp_path, vault_path, monkeypatch):
    monkeypatch.setenv("KEY_A", "alpha")
    monkeypatch.setenv("KEY_B", "beta")
    monkeypatch.setenv("KEY_C", "gamma")

    count = import_from_os_env(vault_path, PASSWORD, keys=["KEY_A", "KEY_C"])
    assert count == 2

    content = unseal(vault_path, PASSWORD)
    variables = parse_env_file(content)
    assert "KEY_A" in variables
    assert "KEY_C" in variables
    assert "KEY_B" not in variables


def test_merge_env_file_adds_new_keys(tmp_path, vault_path):
    initial = tmp_path / "initial.env"
    initial.write_text("ALPHA=1\n")
    import_from_file(initial, vault_path, PASSWORD)

    extra = tmp_path / "extra.env"
    extra.write_text("BETA=2\n")
    result = merge_env_file(extra, vault_path, PASSWORD)

    assert result["added"] == 1
    assert result["skipped"] == 0

    content = unseal(vault_path, PASSWORD)
    variables = parse_env_file(content)
    assert variables["ALPHA"] == "1"
    assert variables["BETA"] == "2"


def test_merge_env_file_skips_existing_without_overwrite(tmp_path, vault_path):
    initial = tmp_path / "initial.env"
    initial.write_text("ALPHA=original\n")
    import_from_file(initial, vault_path, PASSWORD)

    update = tmp_path / "update.env"
    update.write_text("ALPHA=new_value\n")
    result = merge_env_file(update, vault_path, PASSWORD, overwrite=False)

    assert result["skipped"] == 1
    content = unseal(vault_path, PASSWORD)
    assert parse_env_file(content)["ALPHA"] == "original"


def test_merge_env_file_overwrites_when_flag_set(tmp_path, vault_path):
    initial = tmp_path / "initial.env"
    initial.write_text("ALPHA=original\n")
    import_from_file(initial, vault_path, PASSWORD)

    update = tmp_path / "update.env"
    update.write_text("ALPHA=updated\n")
    result = merge_env_file(update, vault_path, PASSWORD, overwrite=True)

    assert result["added"] == 1
    content = unseal(vault_path, PASSWORD)
    assert parse_env_file(content)["ALPHA"] == "updated"
