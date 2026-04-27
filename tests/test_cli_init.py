"""Integration tests for the `envault init` CLI command."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.config import CONFIG_FILENAME


@pytest.fixture()
def runner():
    return CliRunner()


def test_init_creates_config_file(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0, result.output
        assert Path(CONFIG_FILENAME).exists()


def test_init_output_mentions_vault_dir(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "--vault-dir", "my_secrets"])
        assert "my_secrets" in result.output


def test_init_custom_env_file(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "--env-file", ".env.prod"])
        assert result.exit_code == 0
        data = json.loads(Path(CONFIG_FILENAME).read_text())
        assert data["default_env_file"] == ".env.prod"


def test_init_default_vault_dir(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(cli, ["init"])
        data = json.loads(Path(CONFIG_FILENAME).read_text())
        assert data["vault_dir"] == ".envault"


def test_init_idempotent(runner, tmp_path):
    """Running init twice should overwrite without error."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(cli, ["init"])
        result = runner.invoke(cli, ["init", "--vault-dir", "new_dir"])
        assert result.exit_code == 0
        data = json.loads(Path(CONFIG_FILENAME).read_text())
        assert data["vault_dir"] == "new_dir"
