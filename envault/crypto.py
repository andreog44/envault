"""Encryption and decryption utilities for envault using Fernet symmetric encryption."""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT_SIZE = 16
ITERATIONS = 390000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(plaintext: str, password: str) -> bytes:
    """Encrypt plaintext string with a password. Returns salt + ciphertext."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    fernet = Fernet(key)
    ciphertext = fernet.encrypt(plaintext.encode())
    return salt + ciphertext


def decrypt(data: bytes, password: str) -> str:
    """Decrypt data (salt + ciphertext) with a password. Returns plaintext string."""
    salt = data[:SALT_SIZE]
    ciphertext = data[SALT_SIZE:]
    key = derive_key(password, salt)
    fernet = Fernet(key)
    try:
        return fernet.decrypt(ciphertext).decode()
    except InvalidToken as e:
        raise ValueError("Decryption failed: invalid password or corrupted data.") from e
