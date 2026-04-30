"""Tests for envault.pinning."""

import pytest
from pathlib import Path

from envault.vault import Vault
from envault.pinning import (
    PinningError,
    pin_secret,
    get_pin,
    list_pins,
    delete_pin,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    path = tmp_path / "vault.json"
    v = Vault(path, PASSWORD)
    v.set("DB_URL", "postgres://localhost/dev")
    v.set("API_KEY", "secret-api-key")
    return path


def test_pin_secret_returns_entry(vault_path):
    entry = pin_secret(vault_path, PASSWORD, "DB_URL", "v1")
    assert entry["label"] == "v1"
    assert entry["value"] == "postgres://localhost/dev"
    assert "pinned_at" in entry


def test_get_pin_returns_value(vault_path):
    pin_secret(vault_path, PASSWORD, "DB_URL", "stable")
    value = get_pin(vault_path, "DB_URL", "stable")
    assert value == "postgres://localhost/dev"


def test_get_pin_unknown_label_returns_none(vault_path):
    assert get_pin(vault_path, "DB_URL", "nonexistent") is None


def test_get_pin_unknown_key_returns_none(vault_path):
    assert get_pin(vault_path, "MISSING_KEY", "v1") is None


def test_pin_missing_key_raises(vault_path):
    with pytest.raises(PinningError, match="not found"):
        pin_secret(vault_path, PASSWORD, "DOES_NOT_EXIST", "v1")


def test_duplicate_label_raises(vault_path):
    pin_secret(vault_path, PASSWORD, "DB_URL", "v1")
    with pytest.raises(PinningError, match="already exists"):
        pin_secret(vault_path, PASSWORD, "DB_URL", "v1")


def test_empty_label_raises(vault_path):
    with pytest.raises(PinningError, match="empty"):
        pin_secret(vault_path, PASSWORD, "DB_URL", "")


def test_list_pins_sorted_by_pinned_at(vault_path):
    pin_secret(vault_path, PASSWORD, "DB_URL", "v1")
    pin_secret(vault_path, PASSWORD, "DB_URL", "v2")
    pins = list_pins(vault_path, "DB_URL")
    assert [p["label"] for p in pins] == ["v1", "v2"]


def test_list_pins_empty_for_unknown_key(vault_path):
    assert list_pins(vault_path, "UNKNOWN") == []


def test_delete_pin_returns_true(vault_path):
    pin_secret(vault_path, PASSWORD, "API_KEY", "release")
    result = delete_pin(vault_path, "API_KEY", "release")
    assert result is True
    assert get_pin(vault_path, "API_KEY", "release") is None


def test_delete_nonexistent_pin_returns_false(vault_path):
    assert delete_pin(vault_path, "DB_URL", "ghost") is False


def test_pin_survives_vault_value_change(vault_path):
    pin_secret(vault_path, PASSWORD, "DB_URL", "before")
    v = Vault(vault_path, PASSWORD)
    v.set("DB_URL", "postgres://newhost/prod")
    assert get_pin(vault_path, "DB_URL", "before") == "postgres://localhost/dev"
