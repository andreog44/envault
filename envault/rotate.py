"""Password rotation for encrypted vault files."""

from pathlib import Path
from envault.crypto import encrypt, decrypt
from envault.vault import get_vault_path


def rotate_password(
    project_dir: Path,
    old_password: str,
    new_password: str,
    profile: str = "default",
) -> Path:
    """Re-encrypt a vault file with a new password.

    Decrypts the vault using the old password, then re-encrypts
    the plaintext with the new password in-place.

    Args:
        project_dir: Root directory of the project.
        old_password: Current encryption password.
        new_password: Replacement encryption password.
        profile: Vault profile name (default: "default").

    Returns:
        Path to the rotated vault file.

    Raises:
        FileNotFoundError: If the vault file does not exist.
        ValueError: If the old password is incorrect.
    """
    vault_path = get_vault_path(project_dir, profile)

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    ciphertext = vault_path.read_bytes()

    try:
        plaintext = decrypt(ciphertext, old_password)
    except Exception as exc:
        raise ValueError("Old password is incorrect or vault is corrupted.") from exc

    new_ciphertext = encrypt(plaintext, new_password)
    vault_path.write_bytes(new_ciphertext)

    return vault_path


def backup_vault(project_dir: Path, profile: str = "default") -> Path:
    """Create a timestamped backup of the vault file before rotation.

    Args:
        project_dir: Root directory of the project.
        profile: Vault profile name.

    Returns:
        Path to the backup file.

    Raises:
        FileNotFoundError: If the vault file does not exist.
    """
    import shutil
    from datetime import datetime

    vault_path = get_vault_path(project_dir, profile)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    backup_path = vault_path.with_suffix(f".{timestamp}.bak")
    shutil.copy2(vault_path, backup_path)
    return backup_path
