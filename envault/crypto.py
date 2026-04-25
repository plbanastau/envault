"""Encryption and decryption utilities for envault."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


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


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt plaintext using a password. Returns a base64-encoded token with salt."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(plaintext.encode())
    combined = salt + token
    return base64.urlsafe_b64encode(combined).decode()


def decrypt(ciphertext: str, password: str) -> str:
    """Decrypt a ciphertext token using a password. Raises ValueError on failure."""
    try:
        combined = base64.urlsafe_b64decode(ciphertext.encode())
        salt = combined[:SALT_SIZE]
        token = combined[SALT_SIZE:]
        key = derive_key(password, salt)
        f = Fernet(key)
        return f.decrypt(token).decode()
    except (InvalidToken, Exception) as e:
        raise ValueError(f"Decryption failed: invalid password or corrupted data.") from e
