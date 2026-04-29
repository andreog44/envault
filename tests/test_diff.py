"""Tests for envault.diff module."""

import pytest
from pathlib import Path

from envault.vault import seal
from envault.diff import load_env_vars, diff_vaults, format_diff


ENV_A = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"
ENV_B = "DB_HOST=remotehost\nDB_PORT=5432\nAPI_KEY=xyz789\n"
PASSWORD = "test-password"


@pytest.fixture
def vault_a(tmp_path):
    path = tmp_path / "vault_a.env.vault"
    seal(ENV_A, path, PASSWORD)
    return path


@pytest.fixture
def vault_b(tmp_path):
    path = tmp_path / "vault_b.env.vault"
    seal(ENV_B, path, PASSWORD)
    return path


def test_load_env_vars_returns_dict(vault_a):
    result = load_env_vars(vault_a, PASSWORD)
    assert isinstance(result, dict)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_diff_vaults_detects_added_keys(vault_a, vault_b):
    result = diff_vaults(vault_a, PASSWORD, vault_b)
    assert "API_KEY" in result["added"]
    assert result["added"]["API_KEY"] == "xyz789"


def test_diff_vaults_detects_removed_keys(vault_a, vault_b):
    result = diff_vaults(vault_a, PASSWORD, vault_b)
    assert "SECRET" in result["removed"]


def test_diff_vaults_detects_changed_keys(vault_a, vault_b):
    result = diff_vaults(vault_a, PASSWORD, vault_b)
    assert "DB_HOST" in result["changed"]
    assert result["changed"]["DB_HOST"]["old"] == "localhost"
    assert result["changed"]["DB_HOST"]["new"] == "remotehost"


def test_diff_vaults_detects_unchanged_keys(vault_a, vault_b):
    result = diff_vaults(vault_a, PASSWORD, vault_b)
    assert "DB_PORT" in result["unchanged"]


def test_diff_identical_vaults_shows_no_changes(vault_a):
    result = diff_vaults(vault_a, PASSWORD, vault_a)
    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["changed"] == {}


def test_format_diff_shows_plus_for_added(vault_a, vault_b):
    diff = diff_vaults(vault_a, PASSWORD, vault_b)
    output = format_diff(diff)
    assert "+ API_KEY=xyz789" in output


def test_format_diff_shows_minus_for_removed(vault_a, vault_b):
    diff = diff_vaults(vault_a, PASSWORD, vault_b)
    output = format_diff(diff)
    assert "- SECRET=abc123" in output


def test_format_diff_hides_values_when_requested(vault_a, vault_b):
    diff = diff_vaults(vault_a, PASSWORD, vault_b)
    output = format_diff(diff, hide_values=True)
    assert "xyz789" not in output
    assert "abc123" not in output
    assert "***" in output


def test_format_diff_no_differences_message(vault_a):
    diff = diff_vaults(vault_a, PASSWORD, vault_a)
    output = format_diff(diff)
    assert "No differences found." in output
