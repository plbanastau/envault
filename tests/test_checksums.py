"""Tests for envault.checksums."""

import pytest
from pathlib import Path

from envault.checksums import (
    ChecksumError,
    record_checksum,
    get_checksum,
    verify_checksum,
    delete_checksum,
    list_checksums,
    _hash,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> str:
    return str(tmp_path / "vault.enc")


def test_record_checksum_returns_hex_digest(vault_path):
    digest = record_checksum(vault_path, "API_KEY", "secret123")
    assert isinstance(digest, str)
    assert len(digest) == 64  # SHA-256 hex


def test_record_checksum_matches_manual_hash(vault_path):
    digest = record_checksum(vault_path, "API_KEY", "secret123")
    assert digest == _hash("secret123")


def test_get_checksum_returns_none_for_unknown_key(vault_path):
    assert get_checksum(vault_path, "MISSING") is None


def test_get_checksum_returns_stored_digest(vault_path):
    record_checksum(vault_path, "DB_PASS", "hunter2")
    result = get_checksum(vault_path, "DB_PASS")
    assert result == _hash("hunter2")


def test_verify_checksum_true_for_correct_value(vault_path):
    record_checksum(vault_path, "TOKEN", "abc")
    assert verify_checksum(vault_path, "TOKEN", "abc") is True


def test_verify_checksum_false_for_wrong_value(vault_path):
    record_checksum(vault_path, "TOKEN", "abc")
    assert verify_checksum(vault_path, "TOKEN", "xyz") is False


def test_verify_checksum_false_for_unrecorded_key(vault_path):
    assert verify_checksum(vault_path, "NEVER_SET", "value") is False


def test_delete_checksum_returns_true_when_exists(vault_path):
    record_checksum(vault_path, "KEY", "val")
    assert delete_checksum(vault_path, "KEY") is True


def test_delete_checksum_returns_false_when_missing(vault_path):
    assert delete_checksum(vault_path, "GHOST") is False


def test_delete_checksum_removes_entry(vault_path):
    record_checksum(vault_path, "KEY", "val")
    delete_checksum(vault_path, "KEY")
    assert get_checksum(vault_path, "KEY") is None


def test_list_checksums_empty_before_any_record(vault_path):
    assert list_checksums(vault_path) == {}


def test_list_checksums_returns_all_entries(vault_path):
    record_checksum(vault_path, "A", "1")
    record_checksum(vault_path, "B", "2")
    result = list_checksums(vault_path)
    assert set(result.keys()) == {"A", "B"}
    assert result["A"] == _hash("1")
    assert result["B"] == _hash("2")


def test_record_checksum_empty_key_raises(vault_path):
    with pytest.raises(ChecksumError):
        record_checksum(vault_path, "", "value")


def test_overwrite_updates_digest(vault_path):
    record_checksum(vault_path, "KEY", "old")
    record_checksum(vault_path, "KEY", "new")
    assert verify_checksum(vault_path, "KEY", "new") is True
    assert verify_checksum(vault_path, "KEY", "old") is False
