"""Tests for envault.crypto module."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "supersecret"
PLAINTEXT = "MY_SECRET_VALUE"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert result != PLAINTEXT


def test_decrypt_roundtrip():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(ciphertext, PASSWORD)
    assert recovered == PLAINTEXT


def test_encrypt_produces_unique_tokens():
    """Each encryption should produce a different ciphertext (random salt)."""
    c1 = encrypt(PLAINTEXT, PASSWORD)
    c2 = encrypt(PLAINTEXT, PASSWORD)
    assert c1 != c2


def test_decrypt_with_wrong_password_raises():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(ciphertext, "wrongpassword")


def test_decrypt_corrupted_data_raises():
    with pytest.raises(ValueError):
        decrypt("notvalidbase64data!!", PASSWORD)


def test_encrypt_empty_string():
    ciphertext = encrypt("", PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == ""


def test_encrypt_unicode_content():
    text = "UNICODE=café_naïve"
    ciphertext = encrypt(text, PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == text
