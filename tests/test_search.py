"""Tests for envault.search module."""

import pytest
from pathlib import Path

from envault.vault import seal, get_vault_path
from envault.search import search_keys, search_values

PASSWORD = "test-password"
SAMPLE_ENV = """# Sample env file
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=supersecret
API_KEY=abc123
DEBUG=true
"""


@pytest.fixture
def vault_dir(tmp_path):
    vault_path = get_vault_path(tmp_path)
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    seal(vault_path, SAMPLE_ENV, PASSWORD)
    return tmp_path


def test_search_keys_finds_exact_prefix(vault_dir):
    results = search_keys(vault_dir, r"^DB_", PASSWORD)
    keys = [r["key"] for r in results]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "DB_PASSWORD" in keys
    assert "API_KEY" not in keys


def test_search_keys_case_insensitive_by_default(vault_dir):
    results = search_keys(vault_dir, "db_host", PASSWORD)
    assert any(r["key"] == "DB_HOST" for r in results)


def test_search_keys_case_sensitive(vault_dir):
    results = search_keys(vault_dir, "db_host", PASSWORD, case_sensitive=True)
    assert len(results) == 0


def test_search_keys_returns_value(vault_dir):
    results = search_keys(vault_dir, "^API_KEY$", PASSWORD)
    assert len(results) == 1
    assert results[0]["value"] == "abc123"


def test_search_keys_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        search_keys(tmp_path, "DB", PASSWORD)


def test_search_keys_invalid_regex_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid regex pattern"):
        search_keys(vault_dir, "[invalid", PASSWORD)


def test_search_values_finds_match(vault_dir):
    results = search_values(vault_dir, "localhost", PASSWORD)
    assert len(results) == 1
    assert results[0]["key"] == "DB_HOST"


def test_search_values_no_match(vault_dir):
    results = search_values(vault_dir, "nonexistent_value_xyz", PASSWORD)
    assert results == []


def test_search_values_includes_vault_path(vault_dir):
    results = search_values(vault_dir, "true", PASSWORD)
    assert len(results) == 1
    assert "vault" in results[0]
    assert results[0]["vault"].endswith(".vault")


def test_search_keys_no_matches_returns_empty(vault_dir):
    results = search_keys(vault_dir, "^NONEXISTENT_", PASSWORD)
    assert results == []
