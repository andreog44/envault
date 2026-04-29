"""Tests for export CLI commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_export import export_group
from envault.vault import seal, get_vault_path
from envault.config import init_config


PASSWORD = "testpassword"
SAMPLE_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV)
    vault_dir = tmp_path / ".envault"
    vault_dir.mkdir()
    seal(env_file, vault_dir, PASSWORD, profile="default")
    init_config(tmp_path)
    return tmp_path


def test_shell_cmd_outputs_export_statements(runner, project):
    result = runner.invoke(
        export_group,
        ["shell", "--vault-dir", str(project / ".envault"), "--profile", "default"],
        input=PASSWORD + "\n",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert 'export DB_HOST="localhost"' in result.output
    assert 'export DB_PORT="5432"' in result.output


def test_shell_cmd_missing_vault_exits_with_error(runner, tmp_path):
    result = runner.invoke(
        export_group,
        ["shell", "--vault-dir", str(tmp_path / ".envault"), "--profile", "missing"],
        input=PASSWORD + "\n",
    )
    assert result.exit_code != 0 or "Error" in result.output


def test_dotenv_cmd_outputs_dotenv_format(runner, project):
    result = runner.invoke(
        export_group,
        ["dotenv", "--vault-dir", str(project / ".envault"), "--profile", "default"],
        input=PASSWORD + "\n",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert 'DB_HOST="localhost"' in result.output


def test_dotenv_cmd_writes_to_file(runner, project, tmp_path):
    output_file = tmp_path / "exported.env"
    result = runner.invoke(
        export_group,
        [
            "dotenv",
            "--vault-dir", str(project / ".envault"),
            "--profile", "default",
            "--output", str(output_file),
        ],
        input=PASSWORD + "\n",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert "DB_HOST" in content
    assert "DB_PORT" in content
