"""Tests for envault.vault module."""

import pytest
from pathlib import Path
from envault.vault import Vault


PASSWORD = "vaultpass"


@pytest.fixture
def tmp_vault(tmp_path):
    vault_file = tmp_path / ".envault" / "vault.enc"
    v = Vault(vault_file, PASSWORD)
    v.load()
    return v


def test_set_and_get(tmp_vault):
    tmp_vault.set("DB_HOST", "localhost")
    assert tmp_vault.get("DB_HOST") == "localhost"


def test_get_missing_key_returns_none(tmp_vault):
    assert tmp_vault.get("NONEXISTENT") is None


def test_delete_existing_key(tmp_vault):
    tmp_vault.set("API_KEY", "abc123")
    result = tmp_vault.delete("API_KEY")
    assert result is True
    assert tmp_vault.get("API_KEY") is None


def test_delete_missing_key_returns_false(tmp_vault):
    assert tmp_vault.delete("GHOST_KEY") is False


def test_list_keys(tmp_vault):
    tmp_vault.set("A", "1")
    tmp_vault.set("B", "2")
    keys = tmp_vault.list_keys()
    assert keys == {"A": "1", "B": "2"}


def test_save_and_reload(tmp_path):
    vault_file = tmp_path / "vault.enc"
    v1 = Vault(vault_file, PASSWORD)
    v1.load()
    v1.set("SECRET", "topsecret")
    v1.save()

    v2 = Vault(vault_file, PASSWORD)
    v2.load()
    assert v2.get("SECRET") == "topsecret"


def test_wrong_password_on_load_raises(tmp_path):
    vault_file = tmp_path / "vault.enc"
    v1 = Vault(vault_file, PASSWORD)
    v1.load()
    v1.set("X", "y")
    v1.save()

    v2 = Vault(vault_file, "wrongpassword")
    with pytest.raises(ValueError):
        v2.load()
