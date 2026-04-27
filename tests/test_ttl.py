"""Tests for envault.ttl — per-secret TTL management."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.ttl import (
    TTLError,
    clear_ttl,
    get_ttl,
    is_expired,
    purge_expired,
    set_ttl,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    p.write_text("{}")
    return p


def test_set_ttl_returns_future_timestamp(vault_path):
    before = time.time()
    expires_at = set_ttl(vault_path, "API_KEY", 60)
    after = time.time()
    assert before + 60 <= expires_at <= after + 60


def test_get_ttl_returns_none_for_unknown_key(vault_path):
    assert get_ttl(vault_path, "MISSING") is None


def test_get_ttl_returns_stored_timestamp(vault_path):
    set_ttl(vault_path, "DB_PASS", 120)
    result = get_ttl(vault_path, "DB_PASS")
    assert result is not None
    assert result > time.time()


def test_is_expired_returns_false_for_future_ttl(vault_path):
    set_ttl(vault_path, "TOKEN", 300)
    assert is_expired(vault_path, "TOKEN") is False


def test_is_expired_returns_false_for_no_ttl(vault_path):
    assert is_expired(vault_path, "NO_TTL_KEY") is False


def test_is_expired_returns_true_for_past_ttl(vault_path, monkeypatch):
    set_ttl(vault_path, "OLD_KEY", 60)
    # Simulate time having moved forward past expiry
    monkeypatch.setattr("envault.ttl.time.time", lambda: time.time() + 120)
    assert is_expired(vault_path, "OLD_KEY") is True


def test_clear_ttl_removes_entry(vault_path):
    set_ttl(vault_path, "SECRET", 60)
    removed = clear_ttl(vault_path, "SECRET")
    assert removed is True
    assert get_ttl(vault_path, "SECRET") is None


def test_clear_ttl_returns_false_for_missing_key(vault_path):
    assert clear_ttl(vault_path, "GHOST") is False


def test_set_ttl_raises_for_non_positive_seconds(vault_path):
    with pytest.raises(TTLError):
        set_ttl(vault_path, "KEY", 0)
    with pytest.raises(TTLError):
        set_ttl(vault_path, "KEY", -10)


def test_purge_expired_removes_expired_keys(vault_path, monkeypatch):
    set_ttl(vault_path, "EXPIRED_A", 60)
    set_ttl(vault_path, "EXPIRED_B", 60)
    set_ttl(vault_path, "ALIVE", 300)
    monkeypatch.setattr("envault.ttl.time.time", lambda: time.time() + 120)
    purged = purge_expired(vault_path)
    assert set(purged) == {"EXPIRED_A", "EXPIRED_B"}
    assert get_ttl(vault_path, "ALIVE") is not None


def test_purge_expired_returns_empty_when_none_expired(vault_path):
    set_ttl(vault_path, "FRESH", 600)
    purged = purge_expired(vault_path)
    assert purged == []
