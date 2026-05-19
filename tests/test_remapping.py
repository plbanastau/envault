"""Tests for envault.remapping."""

import pytest

from envault.remapping import (
    RemappingError,
    apply_remaps,
    get_remap,
    list_remaps,
    remove_remap,
    set_remap,
)


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_set_and_get_remap(vault_path):
    set_remap(vault_path, "DB_PASS", "DATABASE_PASSWORD")
    assert get_remap(vault_path, "DB_PASS") == "DATABASE_PASSWORD"


def test_get_remap_returns_none_for_unknown_key(vault_path):
    assert get_remap(vault_path, "MISSING") is None


def test_set_remap_empty_key_raises(vault_path):
    with pytest.raises(RemappingError, match="key must not be empty"):
        set_remap(vault_path, "", "TARGET")


def test_set_remap_empty_target_raises(vault_path):
    with pytest.raises(RemappingError, match="target must not be empty"):
        set_remap(vault_path, "KEY", "")


def test_set_remap_overwrites_existing(vault_path):
    set_remap(vault_path, "KEY", "FIRST")
    set_remap(vault_path, "KEY", "SECOND")
    assert get_remap(vault_path, "KEY") == "SECOND"


def test_remove_remap_returns_true(vault_path):
    set_remap(vault_path, "KEY", "TARGET")
    assert remove_remap(vault_path, "KEY") is True
    assert get_remap(vault_path, "KEY") is None


def test_remove_remap_missing_key_returns_false(vault_path):
    assert remove_remap(vault_path, "GHOST") is False


def test_list_remaps_empty(vault_path):
    assert list_remaps(vault_path) == {}


def test_list_remaps_sorted(vault_path):
    set_remap(vault_path, "Z_KEY", "Z_TARGET")
    set_remap(vault_path, "A_KEY", "A_TARGET")
    keys = list(list_remaps(vault_path).keys())
    assert keys == sorted(keys)


def test_apply_remaps_renames_key(vault_path):
    set_remap(vault_path, "DB_PASS", "DATABASE_PASSWORD")
    result = apply_remaps(vault_path, {"DB_PASS": "secret", "API_KEY": "abc"})
    assert "DATABASE_PASSWORD" in result
    assert result["DATABASE_PASSWORD"] == "secret"
    assert "DB_PASS" not in result


def test_apply_remaps_keeps_unmapped_keys(vault_path):
    set_remap(vault_path, "X", "Y")
    result = apply_remaps(vault_path, {"X": "1", "UNCHANGED": "2"})
    assert result["UNCHANGED"] == "2"


def test_apply_remaps_empty_mapping(vault_path):
    secrets = {"A": "1", "B": "2"}
    assert apply_remaps(vault_path, secrets) == secrets


def test_set_remap_returns_entry(vault_path):
    entry = set_remap(vault_path, "SRC", "DST")
    assert entry == {"key": "SRC", "target": "DST"}
