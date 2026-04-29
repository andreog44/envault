"""Tests for envault.rotate and envault.cli_rotate."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.vault import seal
from envault.crypto import decrypt
from envault.rotate import rotate_password, backup_vault
from envault.cli_rotate import rotate_group


PLAINTEXT = b"SECRET=hello\nANOTHER=world\n"
OLD_PASS = "old-secret"
NEW_PASS = "new-secret"


@pytest.fixture()
def vault_dir(tmp_path):
    seal(tmp_path, PLAINTEXT, OLD_PASS)
    return tmp_path


def test_rotate_password_decrypts_with_new_password(vault_dir):
    rotate_password(vault_dir, OLD_PASS, NEW_PASS)
    from envault.vault import get_vault_path
    ciphertext = get_vault_path(vault_dir).read_bytes()
    recovered = decrypt(ciphertext, NEW_PASS)
    assert recovered == PLAINTEXT


def test_rotate_password_old_password_no_longer_works(vault_dir):
    rotate_password(vault_dir, OLD_PASS, NEW_PASS)
    from envault.vault import get_vault_path
    ciphertext = get_vault_path(vault_dir).read_bytes()
    with pytest.raises(Exception):
        decrypt(ciphertext, OLD_PASS)


def test_rotate_password_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        rotate_password(tmp_path, OLD_PASS, NEW_PASS)


def test_rotate_password_wrong_old_password_raises(vault_dir):
    with pytest.raises(ValueError, match="incorrect"):
        rotate_password(vault_dir, "wrong-pass", NEW_PASS)


def test_backup_vault_creates_bak_file(vault_dir):
    bak = backup_vault(vault_dir)
    assert bak.suffix == ".bak"
    assert bak.exists()


def test_backup_vault_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        backup_vault(tmp_path)


def test_cli_rotate_password_success(vault_dir):
    runner = CliRunner()
    result = runner.invoke(
        rotate_group,
        ["password", "--project-dir", str(vault_dir), "--no-backup"],
        input=f"{OLD_PASS}\n{NEW_PASS}\n{NEW_PASS}\n",
    )
    assert result.exit_code == 0
    assert "rotated successfully" in result.output


def test_cli_rotate_password_wrong_old_password(vault_dir):
    runner = CliRunner()
    result = runner.invoke(
        rotate_group,
        ["password", "--project-dir", str(vault_dir), "--no-backup"],
        input=f"wrong\n{NEW_PASS}\n{NEW_PASS}\n",
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_rotate_creates_backup_by_default(vault_dir):
    runner = CliRunner()
    result = runner.invoke(
        rotate_group,
        ["password", "--project-dir", str(vault_dir)],
        input=f"{OLD_PASS}\n{NEW_PASS}\n{NEW_PASS}\n",
    )
    assert result.exit_code == 0
    assert "Backup created" in result.output
