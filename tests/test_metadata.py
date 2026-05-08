"""Tests for envault.metadata."""

from __future__ import annotations

import pytest

from envault.metadata import (
    MetadataError,
    get_all_meta,
    get_meta,
    list_meta_keys,
    remove_meta,
    set_meta,
)


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "vault.enc")


def test_set_and_get_meta(vault_path):
    set_meta(vault_path, "DB_PASSWORD", "owner", "alice")
    assert get_meta(vault_path, "DB_PASSWORD", "owner") == "alice"


def test_get_meta_returns_none_for_unknown_key(vault_path):
    assert get_meta(vault_path, "MISSING", "owner") is None


def test_get_meta_returns_none_for_unknown_field(vault_path):
    set_meta(vault_path, "API_KEY", "owner", "bob")
    assert get_meta(vault_path, "API_KEY", "description") is None


def test_set_meta_overwrites_existing_field(vault_path):
    set_meta(vault_path, "TOKEN", "env", "staging")
    set_meta(vault_path, "TOKEN", "env", "production")
    assert get_meta(vault_path, "TOKEN", "env") == "production"


def test_set_meta_stores_multiple_fields(vault_path):
    set_meta(vault_path, "SECRET", "owner", "carol")
    set_meta(vault_path, "SECRET", "env", "prod")
    meta = get_all_meta(vault_path, "SECRET")
    assert meta == {"owner": "carol", "env": "prod"}


def test_get_all_meta_returns_empty_for_unknown_key(vault_path):
    assert get_all_meta(vault_path, "NOPE") == {}


def test_set_meta_returns_updated_dict(vault_path):
    result = set_meta(vault_path, "KEY", "note", "important")
    assert result == {"note": "important"}


def test_remove_meta_existing_field_returns_true(vault_path):
    set_meta(vault_path, "DB_URL", "owner", "dave")
    assert remove_meta(vault_path, "DB_URL", "owner") is True
    assert get_meta(vault_path, "DB_URL", "owner") is None


def test_remove_meta_missing_field_returns_false(vault_path):
    assert remove_meta(vault_path, "GHOST", "owner") is False


def test_remove_meta_cleans_up_empty_key_entry(vault_path):
    set_meta(vault_path, "SOLO", "x", 1)
    remove_meta(vault_path, "SOLO", "x")
    assert "SOLO" not in list_meta_keys(vault_path)


def test_list_meta_keys_empty_before_any_set(vault_path):
    assert list_meta_keys(vault_path) == []


def test_list_meta_keys_sorted(vault_path):
    set_meta(vault_path, "Z_KEY", "a", 1)
    set_meta(vault_path, "A_KEY", "a", 1)
    set_meta(vault_path, "M_KEY", "a", 1)
    assert list_meta_keys(vault_path) == ["A_KEY", "M_KEY", "Z_KEY"]


def test_set_meta_empty_key_raises(vault_path):
    with pytest.raises(MetadataError, match="key"):
        set_meta(vault_path, "", "field", "val")


def test_set_meta_empty_field_raises(vault_path):
    with pytest.raises(MetadataError, match="field"):
        set_meta(vault_path, "KEY", "", "val")


def test_meta_value_can_be_non_string(vault_path):
    set_meta(vault_path, "NUM", "priority", 42)
    assert get_meta(vault_path, "NUM", "priority") == 42
