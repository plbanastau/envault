"""Tests for envault/encoding.py."""

import pytest

from envault.encoding import (
    EncodingError,
    decode_value,
    encode_value,
    get_encoding,
    remove_encoding,
    set_encoding,
)


@pytest.fixture()
def vault_path(tmp_path):
    return tmp_path / "vault.db"


# --- set / get ---

def test_set_and_get_encoding(vault_path):
    set_encoding(vault_path, "API_KEY", "base64")
    assert get_encoding(vault_path, "API_KEY") == "base64"


def test_get_encoding_returns_none_for_unknown_key(vault_path):
    assert get_encoding(vault_path, "MISSING") is None


def test_set_encoding_overwrites_existing(vault_path):
    set_encoding(vault_path, "TOKEN", "utf8")
    set_encoding(vault_path, "TOKEN", "hex")
    assert get_encoding(vault_path, "TOKEN") == "hex"


def test_set_encoding_returns_encoding_name(vault_path):
    result = set_encoding(vault_path, "SECRET", "base64")
    assert result == "base64"


def test_set_encoding_empty_key_raises(vault_path):
    with pytest.raises(EncodingError, match="key must not be empty"):
        set_encoding(vault_path, "", "utf8")


def test_set_encoding_invalid_format_raises(vault_path):
    with pytest.raises(EncodingError, match="unsupported encoding"):
        set_encoding(vault_path, "KEY", "rot13")


# --- remove ---

def test_remove_encoding_returns_true_when_exists(vault_path):
    set_encoding(vault_path, "KEY", "hex")
    assert remove_encoding(vault_path, "KEY") is True
    assert get_encoding(vault_path, "KEY") is None


def test_remove_encoding_returns_false_when_missing(vault_path):
    assert remove_encoding(vault_path, "GHOST") is False


# --- encode_value / decode_value ---

def test_encode_utf8_is_identity():
    assert encode_value("hello", "utf8") == "hello"


def test_encode_base64_roundtrip():
    original = "super_secret_value"
    encoded = encode_value(original, "base64")
    assert encoded != original
    assert decode_value(encoded, "base64") == original


def test_encode_hex_roundtrip():
    original = "another_value"
    encoded = encode_value(original, "hex")
    assert encoded != original
    assert decode_value(encoded, "hex") == original


def test_encode_unknown_encoding_raises():
    with pytest.raises(EncodingError, match="unknown encoding"):
        encode_value("value", "binary")


def test_decode_unknown_encoding_raises():
    with pytest.raises(EncodingError, match="unknown encoding"):
        decode_value("value", "binary")


def test_multiple_keys_independent(vault_path):
    set_encoding(vault_path, "A", "base64")
    set_encoding(vault_path, "B", "hex")
    assert get_encoding(vault_path, "A") == "base64"
    assert get_encoding(vault_path, "B") == "hex"
