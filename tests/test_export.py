"""Tests for envault.export module."""

import os
import pytest
from pathlib import Path

from envault.vault import seal, get_vault_path
from envault.export import parse_env_file, export_to_shell, export_to_dict, inject_into_env


SAMPLE_ENV = """# This is a comment
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY="my_secret"
EMPTY_VALUE=
APP_NAME='myapp'
"""

PASSWORD = "testpassword"


@pytest.fixture
def vault_path(tmp_path):
    vault_dir = tmp_path / ".envault"
    vault_dir.mkdir()
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV)
    seal(env_file, vault_dir, PASSWORD, profile="default")
    return get_vault_path(vault_dir, "default")


def test_parse_env_file_ignores_comments():
    result = parse_env_file(SAMPLE_ENV)
    assert "#" not in str(result.keys())


def test_parse_env_file_parses_key_value():
    result = parse_env_file(SAMPLE_ENV)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_parse_env_file_strips_quotes():
    result = parse_env_file(SAMPLE_ENV)
    assert result["SECRET_KEY"] == "my_secret"
    assert result["APP_NAME"] == "myapp"


def test_parse_env_file_handles_empty_value():
    result = parse_env_file(SAMPLE_ENV)
    assert result["EMPTY_VALUE"] == ""


def test_export_to_shell_returns_export_statements(vault_path):
    output = export_to_shell(vault_path, PASSWORD)
    assert 'export DB_HOST="localhost"' in output
    assert 'export DB_PORT="5432"' in output


def test_export_to_dict_returns_dict(vault_path):
    result = export_to_dict(vault_path, PASSWORD)
    assert isinstance(result, dict)
    assert result["DB_HOST"] == "localhost"


def test_export_to_dict_wrong_password_raises(vault_path):
    with pytest.raises(Exception):
        export_to_dict(vault_path, "wrongpassword")


def test_inject_into_env_sets_os_environ(vault_path):
    os.environ.pop("DB_HOST", None)
    injected = inject_into_env(vault_path, PASSWORD)
    assert "DB_HOST" in injected
    assert os.environ["DB_HOST"] == "localhost"


def test_inject_into_env_no_overwrite(vault_path):
    os.environ["DB_HOST"] = "original"
    inject_into_env(vault_path, PASSWORD, overwrite=False)
    assert os.environ["DB_HOST"] == "original"
    os.environ.pop("DB_HOST", None)


def test_inject_into_env_with_overwrite(vault_path):
    os.environ["DB_HOST"] = "original"
    inject_into_env(vault_path, PASSWORD, overwrite=True)
    assert os.environ["DB_HOST"] == "localhost"
    os.environ.pop("DB_HOST", None)
