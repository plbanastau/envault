"""Tests for envault.locking."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.locking import (
    LockError,
    acquire,
    is_locked,
    lock_info,
    release,
    _lock_path,
    STALE_LOCK_SECONDS,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    vp = tmp_path / "test.vault"
    vp.write_text("{}")
    return vp


def test_acquire_creates_lock_file(vault_path):
    acquire(vault_path)
    assert _lock_path(vault_path).exists()
    release(vault_path)  # cleanup


def test_is_locked_false_before_acquire(vault_path):
    assert is_locked(vault_path) is False


def test_is_locked_true_after_acquire(vault_path):
    acquire(vault_path)
    assert is_locked(vault_path) is True
    release(vault_path)


def test_is_locked_false_after_release(vault_path):
    acquire(vault_path)
    release(vault_path)
    assert is_locked(vault_path) is False


def test_release_raises_when_not_locked(vault_path):
    with pytest.raises(LockError, match="No lock file"):
        release(vault_path)


def test_acquire_times_out_when_already_locked(vault_path):
    acquire(vault_path, owner="first")
    with pytest.raises(LockError, match="Could not acquire lock"):
        acquire(vault_path, owner="second", timeout=0.1)
    release(vault_path)


def test_lock_info_returns_none_when_not_locked(vault_path):
    assert lock_info(vault_path) is None


def test_lock_info_contains_expected_fields(vault_path):
    acquire(vault_path, owner="ci-runner")
    info = lock_info(vault_path)
    assert info is not None
    assert info["owner"] == "ci-runner"
    assert "acquired_at" in info
    assert "pid" in info
    release(vault_path)


def test_stale_lock_is_cleared_on_next_acquire(vault_path):
    import json

    stale_time = time.time() - (STALE_LOCK_SECONDS + 5)
    _lock_path(vault_path).write_text(
        json.dumps({"owner": "ghost", "acquired_at": stale_time, "pid": 0})
    )
    # Should succeed because the lock is stale
    acquire(vault_path, owner="new-owner", timeout=1.0)
    info = lock_info(vault_path)
    assert info["owner"] == "new-owner"
    release(vault_path)


def test_is_locked_returns_false_for_stale_lock(vault_path):
    import json

    stale_time = time.time() - (STALE_LOCK_SECONDS + 1)
    _lock_path(vault_path).write_text(
        json.dumps({"owner": "ghost", "acquired_at": stale_time, "pid": 0})
    )
    assert is_locked(vault_path) is False
