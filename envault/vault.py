"""Vault file read/write operations for envault."""

import os
from pathlib import Path
from envault.crypto import encrypt, decrypt

VAULT_EXTENSION = ".vault"


def get_vault_path(env_path: str | Path) -> Path:
    """Return the vault file path corresponding to an env file path."""
    env_path = Path(env_path)
    return env_path.with_suffix(VAULT_EXTENSION)


def seal(env_path: str | Path, password: str, output_path: str | Path | None = None) -> Path:
    """Encrypt an env file and write it as a vault file.

    Args:
        env_path: Path to the plaintext .env file.
        password: Password used for encryption.
        output_path: Optional custom output path for the vault file.

    Returns:
        Path to the created vault file.
    """
    env_path = Path(env_path)
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")

    plaintext = env_path.read_text(encoding="utf-8")
    encrypted = encrypt(plaintext, password)

    vault_path = Path(output_path) if output_path else get_vault_path(env_path)
    vault_path.write_bytes(encrypted)
    return vault_path


def unseal(vault_path: str | Path, password: str, output_path: str | Path | None = None) -> Path:
    """Decrypt a vault file and write it as a plaintext env file.

    Args:
        vault_path: Path to the encrypted .vault file.
        password: Password used for decryption.
        output_path: Optional custom output path for the env file.

    Returns:
        Path to the created env file.
    """
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    data = vault_path.read_bytes()
    plaintext = decrypt(data, password)

    if output_path:
        env_path = Path(output_path)
    else:
        env_path = vault_path.with_suffix(".env")

    env_path.write_text(plaintext, encoding="utf-8")
    return env_path
