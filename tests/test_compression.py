"""Tests for envault.compression."""

from __future__ import annotations

import pytest

from envault.compression import (
    COMPRESSION_MARKER,
    CompressionError,
    CompressionStats,
    compress_secrets,
    compress_value,
    decompress_secrets,
    decompress_value,
    is_compressed,
    list_compressed_keys,
)


# ---------------------------------------------------------------------------
# compress_value / decompress_value
# ---------------------------------------------------------------------------

def test_compress_value_returns_marker_prefix():
    result = compress_value("hello world")
    assert result.startswith(COMPRESSION_MARKER)


def test_decompress_roundtrip():
    original = "DATABASE_URL=postgres://user:pass@localhost/db"
    assert decompress_value(compress_value(original)) == original


def test_decompress_plain_value_unchanged():
    plain = "no compression here"
    assert decompress_value(plain) == plain


def test_compress_empty_string():
    result = compress_value("")
    assert is_compressed(result)
    assert decompress_value(result) == ""


def test_compress_non_string_raises():
    with pytest.raises(CompressionError):
        compress_value(123)  # type: ignore[arg-type]


def test_decompress_corrupted_data_raises():
    bad = COMPRESSION_MARKER + "!!!not-valid-base64!!!"
    with pytest.raises(CompressionError):
        decompress_value(bad)


def test_compress_produces_different_size_for_long_input():
    long_value = "SECRET_" * 200
    compressed = compress_value(long_value)
    assert len(compressed) < len(long_value)


# ---------------------------------------------------------------------------
# is_compressed
# ---------------------------------------------------------------------------

def test_is_compressed_true_for_compressed_value():
    assert is_compressed(compress_value("test"))


def test_is_compressed_false_for_plain_value():
    assert not is_compressed("plain text")


# ---------------------------------------------------------------------------
# CompressionStats
# ---------------------------------------------------------------------------

def test_stats_ratio_zero_original():
    stats = CompressionStats(key="k", original_size=0, compressed_size=0)
    assert stats.ratio == 1.0


def test_stats_saved_bytes():
    stats = CompressionStats(key="k", original_size=100, compressed_size=60)
    assert stats.saved_bytes == 40
    assert stats.ratio == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# compress_secrets / decompress_secrets
# ---------------------------------------------------------------------------

def test_compress_secrets_modifies_dict_in_place():
    secrets = {"A": "alpha", "B": "beta"}
    compress_secrets(secrets)
    assert is_compressed(secrets["A"])
    assert is_compressed(secrets["B"])


def test_compress_secrets_returns_stats_for_all_keys():
    secrets = {"X": "value_x", "Y": "value_y"}
    stats = compress_secrets(secrets)
    assert set(stats.keys()) == {"X", "Y"}
    for s in stats.values():
        assert isinstance(s, CompressionStats)


def test_decompress_secrets_restores_values():
    original = {"DB": "postgres://localhost/mydb", "TOKEN": "abc123"}
    secrets = dict(original)
    compress_secrets(secrets)
    decompress_secrets(secrets)
    assert secrets == original


def test_decompress_secrets_leaves_plain_values_unchanged():
    secrets = {"PLAIN": "no marker here"}
    decompress_secrets(secrets)
    assert secrets["PLAIN"] == "no marker here"


# ---------------------------------------------------------------------------
# list_compressed_keys
# ---------------------------------------------------------------------------

def test_list_compressed_keys_returns_sorted():
    secrets = {"Z": compress_value("z"), "A": compress_value("a"), "M": "plain"}
    result = list_compressed_keys(secrets)
    assert result == ["A", "Z"]


def test_list_compressed_keys_empty_when_none_compressed():
    secrets = {"A": "plain", "B": "also plain"}
    assert list_compressed_keys(secrets) == []
