"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt, SALT_SIZE


PASSWORD = "super-secret-password"
PLAINTEXT = "API_KEY=abc123\nDB_URL=postgres://localhost/mydb\n"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_includes_salt():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert len(result) > SALT_SIZE


def test_decrypt_roundtrip():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == PLAINTEXT


def test_decrypt_wrong_password_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encrypted, "wrong-password")


def test_encrypt_produces_different_ciphertext_each_time():
    """Each encryption call should produce a unique ciphertext due to random salt."""
    enc1 = encrypt(PLAINTEXT, PASSWORD)
    enc2 = encrypt(PLAINTEXT, PASSWORD)
    assert enc1 != enc2


def test_decrypt_corrupted_data_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    corrupted = encrypted[:SALT_SIZE] + b"\x00" * (len(encrypted) - SALT_SIZE)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(corrupted, PASSWORD)
