"""Tests for envault.expiry."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from envault.expiry import (
    ExpiryError,
    get_expiry,
    is_expired,
    list_expiring,
    remove_expiry,
    set_expiry,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    p.write_text("{}")
    return p


def _future(seconds: int = 3600) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(seconds=seconds)


def _past(seconds: int = 3600) -> datetime:
    return datetime.now(tz=timezone.utc) - timedelta(seconds=seconds)


def test_set_expiry_returns_iso_string(vault_path):
    ts = set_expiry(vault_path, "API_KEY", _future())
    assert isinstance(ts, str)
    assert "T" in ts and ts.endswith("Z")


def test_get_expiry_returns_none_for_unknown_key(vault_path):
    assert get_expiry(vault_path, "MISSING") is None


def test_get_expiry_returns_stored_datetime(vault_path):
    exp = _future(7200)
    set_expiry(vault_path, "DB_PASS", exp)
    result = get_expiry(vault_path, "DB_PASS")
    assert result is not None
    assert abs((result - exp).total_seconds()) < 2


def test_is_expired_false_for_future(vault_path):
    set_expiry(vault_path, "TOKEN", _future())
    assert is_expired(vault_path, "TOKEN") is False


def test_is_expired_true_for_past(vault_path):
    set_expiry(vault_path, "OLD_KEY", _past())
    assert is_expired(vault_path, "OLD_KEY") is True


def test_is_expired_false_for_key_without_expiry(vault_path):
    assert is_expired(vault_path, "NO_EXPIRY") is False


def test_remove_expiry_returns_true_on_success(vault_path):
    set_expiry(vault_path, "SECRET", _future())
    assert remove_expiry(vault_path, "SECRET") is True
    assert get_expiry(vault_path, "SECRET") is None


def test_remove_expiry_returns_false_when_not_set(vault_path):
    assert remove_expiry(vault_path, "GHOST") is False


def test_list_expiring_empty_before_any_set(vault_path):
    assert list_expiring(vault_path) == []


def test_list_expiring_sorted_soonest_first(vault_path):
    set_expiry(vault_path, "LATER", _future(7200))
    set_expiry(vault_path, "SOONER", _future(1800))
    entries = list_expiring(vault_path)
    assert [e["key"] for e in entries] == ["SOONER", "LATER"]


def test_list_expiring_includes_expired_flag(vault_path):
    set_expiry(vault_path, "ALIVE", _future())
    set_expiry(vault_path, "DEAD", _past())
    entries = {e["key"]: e for e in list_expiring(vault_path)}
    assert entries["ALIVE"]["expired"] is False
    assert entries["DEAD"]["expired"] is True


def test_set_expiry_empty_key_raises(vault_path):
    with pytest.raises(ExpiryError):
        set_expiry(vault_path, "", _future())


def test_set_expiry_naive_datetime_treated_as_utc(vault_path):
    naive = datetime.utcnow() + timedelta(hours=1)
    ts = set_expiry(vault_path, "NAIVE", naive)
    assert ts.endswith("Z")
