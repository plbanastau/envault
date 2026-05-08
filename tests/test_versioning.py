"""Tests for envault.versioning."""

from __future__ import annotations

import pytest

from envault.versioning import (
    VersioningError,
    get_version,
    list_versions,
    purge_versions,
    record_version,
)


@pytest.fixture()
def vault_path(tmp_path):
    return tmp_path / "vault.json"


# ---------------------------------------------------------------------------
# record_version
# ---------------------------------------------------------------------------

def test_record_version_returns_entry(vault_path):
    entry = record_version(vault_path, "DB_URL", "enc:abc123")
    assert entry["version"] == 1
    assert entry["encrypted_value"] == "enc:abc123"
    assert "timestamp" in entry
    assert entry["actor"] == "system"


def test_record_version_increments(vault_path):
    record_version(vault_path, "DB_URL", "enc:v1")
    entry2 = record_version(vault_path, "DB_URL", "enc:v2")
    assert entry2["version"] == 2


def test_record_version_custom_actor(vault_path):
    entry = record_version(vault_path, "API_KEY", "enc:xyz", actor="alice")
    assert entry["actor"] == "alice"


def test_record_version_empty_key_raises(vault_path):
    with pytest.raises(VersioningError, match="key must not be empty"):
        record_version(vault_path, "", "enc:val")


# ---------------------------------------------------------------------------
# list_versions
# ---------------------------------------------------------------------------

def test_list_versions_empty_before_any_recorded(vault_path):
    assert list_versions(vault_path, "MISSING") == []


def test_list_versions_returns_all_entries(vault_path):
    record_version(vault_path, "X", "enc:1")
    record_version(vault_path, "X", "enc:2")
    record_version(vault_path, "X", "enc:3")
    versions = list_versions(vault_path, "X")
    assert len(versions) == 3
    assert [v["version"] for v in versions] == [1, 2, 3]


def test_list_versions_independent_per_key(vault_path):
    record_version(vault_path, "A", "enc:a1")
    record_version(vault_path, "B", "enc:b1")
    record_version(vault_path, "B", "enc:b2")
    assert len(list_versions(vault_path, "A")) == 1
    assert len(list_versions(vault_path, "B")) == 2


# ---------------------------------------------------------------------------
# get_version
# ---------------------------------------------------------------------------

def test_get_version_returns_correct_entry(vault_path):
    record_version(vault_path, "K", "enc:first")
    record_version(vault_path, "K", "enc:second")
    assert get_version(vault_path, "K", 1)["encrypted_value"] == "enc:first"
    assert get_version(vault_path, "K", 2)["encrypted_value"] == "enc:second"


def test_get_version_no_history_raises(vault_path):
    with pytest.raises(VersioningError, match="no versions recorded"):
        get_version(vault_path, "GHOST", 1)


def test_get_version_out_of_range_raises(vault_path):
    record_version(vault_path, "K", "enc:only")
    with pytest.raises(VersioningError, match="out of range"):
        get_version(vault_path, "K", 5)


# ---------------------------------------------------------------------------
# purge_versions
# ---------------------------------------------------------------------------

def test_purge_versions_removes_all(vault_path):
    record_version(vault_path, "P", "enc:1")
    record_version(vault_path, "P", "enc:2")
    removed = purge_versions(vault_path, "P")
    assert removed == 2
    assert list_versions(vault_path, "P") == []


def test_purge_versions_unknown_key_returns_zero(vault_path):
    assert purge_versions(vault_path, "NOPE") == 0


def test_purge_versions_does_not_affect_other_keys(vault_path):
    record_version(vault_path, "A", "enc:a")
    record_version(vault_path, "B", "enc:b")
    purge_versions(vault_path, "A")
    assert len(list_versions(vault_path, "B")) == 1
