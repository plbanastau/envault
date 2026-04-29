"""Tests for envault.aliases."""

import pytest

from envault.aliases import (
    AliasError,
    list_aliases,
    remove_alias,
    resolve,
    reverse_lookup,
    set_alias,
)


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_set_and_resolve_alias(vault_path):
    set_alias(vault_path, "db", "DATABASE_URL")
    assert resolve(vault_path, "db") == "DATABASE_URL"


def test_resolve_unknown_alias_returns_none(vault_path):
    assert resolve(vault_path, "nonexistent") is None


def test_set_alias_empty_name_raises(vault_path):
    with pytest.raises(AliasError, match="Alias name"):
        set_alias(vault_path, "", "DATABASE_URL")


def test_set_alias_empty_key_raises(vault_path):
    with pytest.raises(AliasError, match="Target key"):
        set_alias(vault_path, "db", "")


def test_set_alias_same_name_and_key_raises(vault_path):
    with pytest.raises(AliasError, match="must differ"):
        set_alias(vault_path, "DB", "DB")


def test_overwrite_existing_alias(vault_path):
    set_alias(vault_path, "db", "DATABASE_URL")
    set_alias(vault_path, "db", "POSTGRES_DSN")
    assert resolve(vault_path, "db") == "POSTGRES_DSN"


def test_remove_existing_alias(vault_path):
    set_alias(vault_path, "db", "DATABASE_URL")
    assert remove_alias(vault_path, "db") is True
    assert resolve(vault_path, "db") is None


def test_remove_missing_alias_returns_false(vault_path):
    assert remove_alias(vault_path, "ghost") is False


def test_list_aliases_empty(vault_path):
    assert list_aliases(vault_path) == []


def test_list_aliases_sorted(vault_path):
    set_alias(vault_path, "z_key", "Z_SECRET")
    set_alias(vault_path, "a_key", "A_SECRET")
    result = list_aliases(vault_path)
    assert [r["alias"] for r in result] == ["a_key", "z_key"]


def test_list_aliases_structure(vault_path):
    set_alias(vault_path, "token", "API_TOKEN")
    entries = list_aliases(vault_path)
    assert entries[0] == {"alias": "token", "key": "API_TOKEN"}


def test_reverse_lookup_single(vault_path):
    set_alias(vault_path, "db", "DATABASE_URL")
    assert reverse_lookup(vault_path, "DATABASE_URL") == ["db"]


def test_reverse_lookup_multiple(vault_path):
    set_alias(vault_path, "db", "DATABASE_URL")
    set_alias(vault_path, "database", "DATABASE_URL")
    assert reverse_lookup(vault_path, "DATABASE_URL") == ["database", "db"]


def test_reverse_lookup_no_match(vault_path):
    assert reverse_lookup(vault_path, "MISSING_KEY") == []
