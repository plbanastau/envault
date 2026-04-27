"""Tests for envault.snapshot module."""

from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
    SnapshotError,
)


PASSWORD = "test-secret-pass"


@pytest.fixture()
def tmp_vault(tmp_path):
    vault = Vault(tmp_path / "test.vault")
    vault.set("DB_HOST", "localhost", PASSWORD)
    vault.set("DB_PORT", "5432", PASSWORD)
    vault.set("API_KEY", "abc123", PASSWORD)
    return vault


def test_create_snapshot_returns_id(tmp_vault):
    snap_id = create_snapshot(tmp_vault, PASSWORD, label="before-migration")
    assert isinstance(snap_id, str)
    assert len(snap_id) > 0


def test_list_snapshots_empty_before_any_created(tmp_vault):
    assert list_snapshots(tmp_vault.path) == []


def test_list_snapshots_contains_created_entry(tmp_vault):
    snap_id = create_snapshot(tmp_vault, PASSWORD, label="v1")
    snapshots = list_snapshots(tmp_vault.path)
    assert len(snapshots) == 1
    assert snapshots[0]["id"] == snap_id
    assert snapshots[0]["label"] == "v1"
    assert "created_at" in snapshots[0]


def test_list_snapshots_newest_first(tmp_vault):
    id1 = create_snapshot(tmp_vault, PASSWORD, label="first")
    id2 = create_snapshot(tmp_vault, PASSWORD, label="second")
    snapshots = list_snapshots(tmp_vault.path)
    assert snapshots[0]["id"] == id2
    assert snapshots[1]["id"] == id1


def test_restore_snapshot_overwrites_current_values(tmp_vault):
    snap_id = create_snapshot(tmp_vault, PASSWORD)
    # Mutate vault after snapshot
    tmp_vault.set("DB_HOST", "prod-server", PASSWORD)
    tmp_vault.delete("API_KEY")

    restored = restore_snapshot(tmp_vault, PASSWORD, snap_id)

    assert restored == 3
    assert tmp_vault.get("DB_HOST", PASSWORD) == "localhost"
    assert tmp_vault.get("API_KEY", PASSWORD) == "abc123"


def test_restore_nonexistent_snapshot_raises(tmp_vault):
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot(tmp_vault, PASSWORD, "0000000000000")


def test_delete_snapshot_returns_true(tmp_vault):
    snap_id = create_snapshot(tmp_vault, PASSWORD)
    assert delete_snapshot(tmp_vault.path, snap_id) is True
    assert list_snapshots(tmp_vault.path) == []


def test_delete_nonexistent_snapshot_returns_false(tmp_vault):
    assert delete_snapshot(tmp_vault.path, "9999999999999") is False


def test_snapshot_label_defaults_to_empty_string(tmp_vault):
    snap_id = create_snapshot(tmp_vault, PASSWORD)
    snapshots = list_snapshots(tmp_vault.path)
    assert snapshots[0]["label"] == ""
