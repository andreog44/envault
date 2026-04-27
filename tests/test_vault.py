"""Tests for envault.vault seal/unseal file operations."""

import pytest
from pathlib import Path
from envault.vault import seal, unseal, get_vault_path, VAULT_EXTENSION


ENV_CONTENT = "SECRET=hello\nANOTHER_VAR=world\n"
PASSWORD = "test-password-123"


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(ENV_CONTENT, encoding="utf-8")
    return p


def test_get_vault_path(tmp_path):
    env = tmp_path / ".env"
    vault = get_vault_path(env)
    assert vault.suffix == VAULT_EXTENSION


def test_seal_creates_vault_file(env_file, tmp_path):
    vault_path = seal(env_file, PASSWORD)
    assert vault_path.exists()
    assert vault_path.suffix == VAULT_EXTENSION


def test_seal_vault_is_not_plaintext(env_file):
    vault_path = seal(env_file, PASSWORD)
    raw = vault_path.read_bytes()
    assert ENV_CONTENT.encode() not in raw


def test_unseal_recovers_original_content(env_file, tmp_path):
    vault_path = seal(env_file, PASSWORD)
    out_path = tmp_path / "recovered.env"
    result = unseal(vault_path, PASSWORD, output_path=out_path)
    assert result.read_text(encoding="utf-8") == ENV_CONTENT


def test_seal_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        seal(tmp_path / "nonexistent.env", PASSWORD)


def test_unseal_wrong_password_raises(env_file):
    vault_path = seal(env_file, PASSWORD)
    with pytest.raises(ValueError):
        unseal(vault_path, "bad-password")
